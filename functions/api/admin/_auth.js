export function hex(buf){return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,'0')).join('')}
export async function sha(s){return hex(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))}
export async function derive(password,salt){const base=await crypto.subtle.importKey('raw',new TextEncoder().encode(password),'PBKDF2',false,['deriveBits']);return hex(await crypto.subtle.deriveBits({name:'PBKDF2',salt:new TextEncoder().encode(salt),iterations:210000,hash:'SHA-256'},base,256))}
export async function authorized(request,env){const token=request.headers.get('Cookie')?.match(/(?:^|;\s*)admin_session=([^;]+)/)?.[1];if(!token)return false;const hash=await sha(token);return !!await env.DB.prepare('SELECT token_hash FROM sessions WHERE token_hash=? AND expires>?').bind(hash,Date.now()).first()}
export function fail(){return Response.json({error:'غير مصرح'},{status:401})}
