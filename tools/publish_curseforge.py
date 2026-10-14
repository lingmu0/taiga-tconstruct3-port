"""Upload verified release jars to an explicitly supplied TAIGA CurseForge project.

Reads CURSEFORGE_UPLOAD_TOKEN only from process environment. It never logs or
stores credentials. Project creation/comment/distribution settings are managed
in the CurseForge author dashboard, not the documented file-upload API.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://minecraft.curseforge.com'

def request(path, token, data=None, content_type=None):
    headers = {'X-Api-Token':token, 'User-Agent':'TAIGA-Forge-Port-Release/1.0'}
    if content_type: headers['Content-Type'] = content_type
    req = urllib.request.Request(BASE+path,data=data,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # Do not echo response bodies: authentication proxies may include request details.
        raise RuntimeError('CurseForge HTTP '+str(error.code)+' for '+path) from None

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-id',type=int)
    parser.add_argument('--publish',action='store_true')
    parser.add_argument('--check-api',action='store_true')
    args = parser.parse_args()
    token = os.environ.get('CURSEFORGE_UPLOAD_TOKEN')
    if not token: raise RuntimeError('CURSEFORGE_UPLOAD_TOKEN is not set')
    if args.check_api:
        versions = request('/api/game/versions',token)
        relevant = [v for v in versions if v['name'] in ('1.18.2','1.19.2','1.20.1','Forge','Client','Server')]
        print(json.dumps(relevant,ensure_ascii=False,indent=2))
        return
    if not args.project_id or args.project_id <= 0: raise RuntimeError('The new TAIGA project ID is required; do not use another mod project ID.')
    version = json.loads((ROOT/'config/compatibility.json').read_text())['mod_version']
    changelog = (ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
    changelog += '\n\nConfiguration: https://github.com/lingmu0/taiga-tconstruct3-port/blob/main/CONFIGURATION.md\n'
    changelog += '\nMatching source: https://github.com/lingmu0/taiga-tconstruct3-port/releases/tag/v'+version+'\n'
    receipts_path = ROOT/'build/publication/curseforge-uploads.local.json'
    receipts = json.loads(receipts_path.read_text()) if receipts_path.exists() else {}
    for mc in ('1.18.2','1.19.2','1.20.1'):
        file = ROOT/f'release/taiga-{mc}-forge-{version}.jar'
        payload = file.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        receipt_key = str(args.project_id)+':'+file.name+':'+digest
        if receipt_key in receipts:
            print('Already uploaded:',file.name,'file ID',receipts[receipt_key]['id'])
            continue
        metadata = {'displayName':'TAIGA '+version+' — Forge '+mc,'changelog':changelog,'changelogType':'markdown',
                    'gameVersionNames':[mc,'Forge','Client','Server'],'releaseType':'beta',
                    'isMarkedForManualRelease':False,
                    'relations':{'projects':[{'slug':slug,'type':'requiredDependency'} for slug in ('tinkers-construct','mantle')]}}
        if not args.publish:
            print('Prepared:',file.name,'project',args.project_id,'SHA256',digest)
            continue
        boundary = 'taiga-'+uuid.uuid4().hex
        content = ('--'+boundary+'\r\nContent-Disposition: form-data; name="metadata"\r\nContent-Type: application/json\r\n\r\n').encode()+json.dumps(metadata).encode()
        content += ('\r\n--'+boundary+'\r\nContent-Disposition: form-data; name="file"; filename="'+file.name+'"\r\nContent-Type: application/java-archive\r\n\r\n').encode()+payload
        content += ('\r\n--'+boundary+'--\r\n').encode()
        result = request('/api/projects/'+str(args.project_id)+'/upload-file',token,content,'multipart/form-data; boundary='+boundary)
        assert isinstance(result.get('id'),int), 'Upload response did not contain a file ID'
        receipts[receipt_key] = {'id':result['id'],'projectId':args.project_id,'file':file.name,'sha256':digest}
        receipts_path.parent.mkdir(parents=True,exist_ok=True)
        receipts_path.write_text(json.dumps(receipts,indent=2)+'\n')
        print('Uploaded:',file.name,'file ID',result['id'])

if __name__ == '__main__': main()
