import {pbkdf2} from './_pbkdf2.js';
export function hex(buf){return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,'0')).join('')}
export async function sha(s){return hex(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))}
export async function derive(password,salt,storedHash){return pbkdf2(password,salt,storedHash?.startsWith('v2:')?12000:210000)}
export async function verifyPassword(password,salt,storedHash){const expected=storedHash?.startsWith('v2:')?storedHash.slice(3):storedHash;return typeof expected==='string' && (await derive(password,salt,storedHash))===expected}
export async function hashNewPassword(password,salt){return 'v2:'+pbkdf2(password,salt,12000)}
export async function authorized(request,env){const token=request.headers.get('Cookie')?.match(/(?:^|;\\s*)admin_session=([^;]+)/)?.[1];if(!token)return false;const hash=await sha(token);return !!await env.DB.prepare('SELECT token_hash FROM sessions WHERE token_hash=? AND expires>?').bind(hash,Date.now()).first()}
export function fail(){return Response.json({error:'غير مصرح'},{status:401})}
