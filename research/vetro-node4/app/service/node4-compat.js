'use strict';
// Small compatibility surface for Samsung's Node 4.4.3 web-service runtime.
var fs = require('fs');
var path = require('path');
var crypto = require('crypto');

if (!Buffer.from) Buffer.from = function (value, encoding) {
    if (typeof value === 'number') throw new TypeError('Buffer.from does not accept a size');
    return new Buffer(value, encoding);
};
if (!Buffer.alloc) Buffer.alloc = function (size, fill, encoding) {
    if (typeof size !== 'number' || size < 0 || Math.floor(size) !== size || size > 0x3fffffff) throw new RangeError('invalid buffer size');
    var buffer = new Buffer(size);
    if (typeof fill === 'string' || Buffer.isBuffer(fill)) {
        var pattern = Buffer.isBuffer(fill) ? fill : Buffer.from(fill, encoding);
        if (!pattern.length) buffer.fill(0);
        else for (var index = 0; index < size; index++) buffer[index] = pattern[index % pattern.length];
    } else buffer.fill(fill === undefined ? 0 : fill);
    return buffer;
};
if (!Object.entries) Object.entries = function (object) {
    return Object.keys(object).map(function (key) { return [key, object[key]]; });
};
if (!Object.values) Object.values = function (object) {
    return Object.keys(object).map(function (key) { return object[key]; });
};
if (!String.prototype.padStart) Object.defineProperty(String.prototype, 'padStart', {configurable: true, writable: true, value: function (length, fill) {
    var text = String(this), padding = fill === undefined ? ' ' : String(fill);
    length = Math.floor(Number(length)) || 0;
    if (!padding || text.length >= length) return text;
    var missing = length - text.length;
    while (padding.length < missing) padding += padding;
    return padding.slice(0, missing) + text;
}});
if (!Array.prototype.includes) Object.defineProperty(Array.prototype, 'includes', {configurable: true, writable: true, value: function (value, from) {
    var length = this.length >>> 0, index = Number(from) || 0;
    if (index < 0) index = Math.max(length + Math.ceil(index), 0);
    for (; index < length; index++) if (this[index] === value || this[index] !== this[index] && value !== value) return true;
    return false;
}});
if (!Promise.prototype.finally) Object.defineProperty(Promise.prototype, 'finally', {configurable: true, writable: true, value: function (callback) {
    if (typeof callback !== 'function') return this.then(callback, callback);
    return this.then(function (value) {
        return Promise.resolve(callback()).then(function () { return value; });
    }, function (error) {
        return Promise.resolve(callback()).then(function () { throw error; });
    });
}});

function mkdirp(directory) {
    try { fs.mkdirSync(directory); }
    catch (error) {
        if (error.code === 'ENOENT') { mkdirp(path.dirname(directory)); fs.mkdirSync(directory); }
        else if (error.code !== 'EEXIST' || !fs.statSync(directory).isDirectory()) throw error;
    }
    return directory;
}

function authenticatorEqual(a, b) {
    if (!Buffer.isBuffer(a) || !Buffer.isBuffer(b) || a.length !== b.length) return false;
    if (crypto.timingSafeEqual) return crypto.timingSafeEqual(a, b);
    // Random-key double HMAC blinds comparison timing. This is not presented as
    // a native constant-time primitive. RNG errors propagate and reject auth.
    var key = crypto.randomBytes(32);
    var left = crypto.createHmac('sha256', key).update(a).digest('hex');
    var right = crypto.createHmac('sha256', key).update(b).digest('hex');
    key.fill(0);
    return left === right;
}

function rsaKeys() {
    if (crypto.generateKeyPairSync) {
        var pair = crypto.generateKeyPairSync('rsa', {modulusLength: 2048});
        return {publicPem: pair.publicKey.export({type: 'spki', format: 'pem'}),
            privatePem: pair.privateKey.export({type: 'pkcs8', format: 'pem'})};
    }
    // Samsung's signed OpenSSL executable; keys remain in memory, not a file.
    var exec = require('child_process').execFileSync;
    var privatePem = exec('/usr/bin/openssl', ['genrsa', '2048'], {timeout: 15000, maxBuffer: 32768, stdio: ['pipe', 'pipe', 'pipe']});
    var publicPem = exec('/usr/bin/openssl', ['rsa', '-pubout'], {input: privatePem, timeout: 5000, maxBuffer: 32768, stdio: ['pipe', 'pipe', 'pipe']});
    return {publicPem: publicPem, privatePem: privatePem};
}
function sign(data, privatePem) {
    return crypto.createSign('RSA-SHA256').update(data).sign(privatePem);
}
module.exports = {mkdirp: mkdirp, authenticatorEqual: authenticatorEqual, rsaKeys: rsaKeys, sign: sign};
