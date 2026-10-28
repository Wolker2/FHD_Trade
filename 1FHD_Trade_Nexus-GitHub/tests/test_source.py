from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile,unittest,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from build import compile_source,load,resource_audit,PREFIX
from gi_codec import encode,decode

class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.files,cls.configs=compile_source()
    def test_complete_hashes_and_resources(self):
        self.assertEqual({name:hashlib.sha256(data).hexdigest() for name,data in self.files.items()},load(ROOT/'original-file-sha256.json'))
        self.assertEqual(len(self.files),61);self.assertEqual(resource_audit(self.files,self.configs)['missing'],[])
        self.assertEqual(self.files['CFG/Rus/Lang.dat'],self.files['CFG/Eng/Lang.dat'])
    def test_pixels_edit_in_all_gi_types(self):
        for name in ['2SearchN','leftButton_D','Goods0N']:
            source=load(ROOT/'SOURCE/Graphics'/(name+'.json'));layer=source['layers'][0]
            if source['type']==0:layer['pixels'][0]^=1
            else:
                packet=next(command for layer in source['layers'] for command in layer.get('commands',[]) if 'pixels' in command)
                packet['pixels'][0]^=1
            self.assertEqual(decode(encode(source)),source,name)
    def test_shared_language_source_edit_is_used(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder);shutil.copytree(ROOT/'SOURCE',target/'SOURCE',ignore=shutil.ignore_patterns('__pycache__'))
            path=target/'SOURCE/CFG/Lang.txt';text=path.read_text('utf-8');self.assertIn('Script',text)
            # Change an existing UI help value rather than compiler/codec state.
            self.assertIn('MarketGoodsFinder',text)
            path.write_text(text.replace('Торгов', 'ТОРГОВ',1),encoding='utf-8')
            edited,_=compile_source(target)
        self.assertEqual(sorted(name for name in edited if edited[name]!=self.files[name]),['CFG/Eng/Lang.dat','CFG/Rus/Lang.dat'])
    def test_retained_supplied_regressions(self):
        for name in ['verify_goods.py','verify_multi.py','verify_requested.py','verify_declarations.py']:
            for language in ['Rus','Eng']:
                p=subprocess.run([sys.executable,str(ROOT/'SOURCE'/name),str(ROOT),language],capture_output=True,text=True)
                self.assertEqual(p.returncode,0,name+' '+language+'\n'+p.stdout+p.stderr)
        for name in ['verify_visibility.py','verify_native_merge.py','verify_render_resources.py']:
            p=subprocess.run([sys.executable,str(ROOT/'SOURCE'/name),str(ROOT)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,name+'\n'+p.stdout+p.stderr)
    def test_isolated_source_only_build(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)
            for name in ['SOURCE','scripts']:
                shutil.copytree(ROOT/name,target/name,ignore=shutil.ignore_patterns('__pycache__'))
            for name in ['build.py','original-file-sha256.json']:shutil.copy2(ROOT/name,target/name)
            self.assertFalse(any(p.suffix.lower() in ['.dat','.gi','.dll','.scr','.exe'] for p in target.rglob('*') if p.is_file()))
            p=subprocess.run([sys.executable,str(target/'build.py'),'--strict-original'],cwd=target,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            with zipfile.ZipFile(target/'dist/FHD_Trade_FROM_SOURCE.zip') as archive:
                self.assertEqual(len(archive.namelist()),61);self.assertIsNone(archive.testzip())
                for name,data in self.files.items():self.assertEqual(archive.read(PREFIX+name),data)
if __name__=='__main__':unittest.main()
