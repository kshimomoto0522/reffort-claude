import base64
with open('gas_shiire_tool.js', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')

js = '(function(){var b64="' + b64 + '";var bin=atob(b64);var bytes=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);var text=new TextDecoder("utf-8").decode(bytes);monaco.editor.getModels()[0].setValue(text);return({chars:text.length,lines:text.split(String.fromCharCode(10)).length});})()'

with open('_inject.js', 'w', encoding='ascii') as f:
    f.write(js)

print(f'Generated: {len(js)} chars')
