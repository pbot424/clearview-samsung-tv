const fs=require('fs'),vm=require('vm'),path=require('path');
let bad=[];
for(const dir of ['app/service','rooting/service']) for(const name of fs.readdirSync(dir).filter(n=>n.endsWith('.js'))) {
 try {new vm.Script(fs.readFileSync(path.join(dir,name),'utf8'));} catch(e){bad.push({file:dir+'/'+name,error:e.message});}
}
console.log(JSON.stringify(bad));
