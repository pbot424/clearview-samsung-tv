'use strict';
require('./node4-compat.js');
// Read only config.xml from a bounded WGT ZIP. No extraction or shell parsing.
var fs = require('fs');
var zlib = require('zlib');
var MAX_WGT = 32 * 1024 * 1024;
var MAX_CONFIG = 65536;
function crc32(data) {
    var crc = 0xffffffff;
    for (var i = 0; i < data.length; i++) {
        crc ^= data[i];
        for (var bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
    }
    return (crc ^ 0xffffffff) >>> 0;
}
function manifestId(xml) {
    if (/<!DOCTYPE|<!ENTITY/i.test(xml)) throw new Error('unsupported XML declarations');
    xml = xml.replace(/<!--[\s\S]*?-->/g, '');
    var namespaces = {};
    var re = /xmlns:([A-Za-z_][\w.-]*)\s*=\s*(["'])(.*?)\2/g, match;
    while ((match = re.exec(xml))) namespaces[match[1]] = match[3];
    var applications = [], tags = /<([A-Za-z_][\w.-]*):application\b([^<>]*)>/g;
    while ((match = tags.exec(xml))) {
        if (namespaces[match[1]] !== 'http://tizen.org/ns/widgets') continue;
        var attrs = match[2], id = /(?:^|\s)package\s*=\s*(["'])(.*?)\1/g;
        var value = id.exec(attrs);
        if (!value || id.exec(attrs) || !/^[A-Za-z0-9_.-]{1,128}$/.test(value[2])) throw new Error('invalid package ID');
        applications.push(value[2]);
    }
    if (applications.length !== 1) throw new Error('expected one Tizen application in config.xml');
    return applications[0];
}
function inflate(data) {
    return new Promise(function (resolve, reject) {
        var stream = zlib.createInflateRaw(), chunks = [], size = 0, settled = false;
        function fail(error) {
            if (settled) return;
            settled = true; chunks = []; stream.destroy(); reject(error);
        }
        stream.on('error', fail);
        stream.on('data', function (chunk) {
            size += chunk.length;
            if (size > MAX_CONFIG) return fail(new Error('config.xml too large'));
            chunks.push(chunk);
        });
        stream.on('end', function () {
            if (!settled) { settled = true; resolve(Buffer.concat(chunks)); }
        });
        stream.end(data);
    });
}
function fromBuffer(zip) {
    return Promise.resolve().then(function () {
    if (zip.length < 22 || zip.length > MAX_WGT) throw new Error('invalid WGT size');
    var end = -1;
    for (var at = zip.length - 22; at >= Math.max(0, zip.length - 65557); at--) {
        if (zip.readUInt32LE(at) === 0x06054b50 && at + 22 + zip.readUInt16LE(at + 20) === zip.length) { end = at; break; }
    }
    if (end < 0 || zip.readUInt16LE(end + 4) || zip.readUInt16LE(end + 6)) throw new Error('unsupported WGT ZIP');
    var count = zip.readUInt16LE(end + 10), size = zip.readUInt32LE(end + 12), offset = zip.readUInt32LE(end + 16);
    if (!count || count > 4096 || zip.readUInt16LE(end + 8) !== count || size > 1048576 || offset + size !== end) throw new Error('invalid ZIP directory');
    var config, configData, configMethod, configSize, configCrc;
    for (var i = 0, pos = offset; i < count; i++) {
        if (pos + 46 > end || zip.readUInt32LE(pos) !== 0x02014b50) throw new Error('invalid ZIP entry');
        var nameLen = zip.readUInt16LE(pos + 28), extra = zip.readUInt16LE(pos + 30), comment = zip.readUInt16LE(pos + 32);
        var next = pos + 46 + nameLen + extra + comment;
        if (next > end) throw new Error('truncated ZIP directory');
        var name = zip.slice(pos + 46, pos + 46 + nameLen).toString('utf8');
        if (name === 'config.xml') {
            if (configData) throw new Error('duplicate config.xml');
            var flags = zip.readUInt16LE(pos + 8), method = zip.readUInt16LE(pos + 10);
            var compressed = zip.readUInt32LE(pos + 20), unpacked = zip.readUInt32LE(pos + 24), local = zip.readUInt32LE(pos + 42);
            if ((flags & 1) || (method !== 0 && method !== 8) || compressed > 262144 || unpacked > MAX_CONFIG) throw new Error('unsupported config.xml encoding or size');
            if (local + 30 > offset || zip.readUInt32LE(local) !== 0x04034b50) throw new Error('invalid config.xml header');
            var localNameLen = zip.readUInt16LE(local + 26), start = local + 30 + localNameLen + zip.readUInt16LE(local + 28);
            if (start + compressed > offset || zip.slice(local + 30, local + 30 + localNameLen).toString('utf8') !== name || zip.readUInt16LE(local + 8) !== method) throw new Error('invalid config.xml location');
            var data = zip.slice(start, start + compressed);
            configData = data; configMethod = method; configSize = unpacked;
            configCrc = zip.readUInt32LE(pos + 16);
        }
        pos = next;
    }
    if (pos !== end || configData == null) throw new Error('missing or invalid config.xml');
    return (configMethod === 8 ? inflate(configData) : Promise.resolve(configData)).then(function (decoded) {
        if (decoded.length !== configSize || crc32(decoded) !== configCrc) throw new Error('config.xml checksum or size mismatch');
        return {packageId: manifestId(decoded.toString('utf8'))};
    });
    });
}
function read(wgtPath) {
    return new Promise(function (resolve, reject) {
        if (typeof wgtPath !== 'string' || !/^\/[A-Za-z0-9_./-]+\.wgt$/.test(wgtPath)) return reject(new Error('expected an absolute .wgt path without spaces or shell characters'));
        fs.open(wgtPath, 'r', function (error, fd) {
            if (error) return reject(error);
            var finished = false;
            function finish(error, result) {
                if (finished) return;
                finished = true;
                fs.close(fd, function (closeError) { if (error || closeError) reject(error || closeError); else resolve(result); });
            }
            fs.fstat(fd, function (error, stat) {
                if (error) return finish(error);
                if (!stat.isFile() || stat.size > MAX_WGT) return finish(new Error('invalid WGT file or size'));
                var data;
                try { data = Buffer.alloc(stat.size); } catch (error) { return finish(error); }
                var at = 0;
                function next() {
                    if (at === data.length) return fromBuffer(data).then(function (result) { finish(null, result); }, finish);
                    fs.read(fd, data, at, data.length - at, at, function (error, count) {
                        if (error) return finish(error);
                        if (!count) return finish(new Error('truncated WGT file'));
                        at += count; next();
                    });
                }
                next();
            });
        });
    });
}
module.exports = {read: read, fromBuffer: fromBuffer, manifestId: manifestId, crc32: crc32};
