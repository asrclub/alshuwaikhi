import {sha,derive} from './_auth.js';
export async function onRequestPost({request,env}){
 let stage='database';
 try{
  if(!env.DB)return Response.json({error:'قاعدة البيانات غير مربوطة',code:'DB_BINDING'},{status:503});
  stage='body';const {username,password}=await request.json();
  if(username!=='admin'||typeof password!=='string'||password.length>200)return Response.json({error:'بيانات غير صحيحة'},{status:401});
  stage='auth_record';const auth=await env.DB.prepare('SELECT salt,password_hash FROM auth WHERE id=1').first();
  if(!auth)return Response.json({error:'حساب المدير غير مُهيأ',code:'AUTH_MISSING'},{status:503});
  stage='password_verify';const hash=await derive(password,auth.salt);
  if(hash!==auth.password_hash)return Response.json({error:'بيانات غير صحيحة'},{status:401});
  stage='session';const token=crypto.randomUUID()+crypto.randomUUID(),tokenHash=await sha(token);
  await env.DB.prepare('INSERT INTO sessions(token_hash,expires) VALUES(?,?)').bind(tokenHash,Date.now()+8*3600*1000).run();
  return new Response(JSON.stringify({ok:true}),{headers:{'Content-Type':'application/json','Set-Cookie':`admin_session=${token}; HttpOnly; Secure; SameSite=Strict; Path=/api/admin; Max-Age=28800`,'Cache-Control':'no-store'}});
 }catch(e){console.error('ADMIN_LOGIN_ERROR',stage,e?.name,e?.message);return Response.json({error:'خطأ بالخادم أثناء تسجيل الدخول',code:'LOGIN_'+stage.toUpperCase(),reason:e?.name||'UNKNOWN'},{status:500,headers:{'Cache-Control':'no-store'}})}
}
