import {authorized,fail,hashNewPassword} from './_auth.js';
export async function onRequestPost({request,env}){
 try{
  if(!await authorized(request,env))return fail();
  const {newPassword}=await request.json();
  if(typeof newPassword!=='string'||newPassword.length<12||newPassword.length>200)return Response.json({error:'كلمة المرور الجديدة يجب أن تكون من ١٢ إلى ٢٠٠ حرف'},{status:400});
  const salt=crypto.randomUUID();
  const hash=await hashNewPassword(newPassword,salt);
  const result=await env.DB.prepare('UPDATE auth SET salt=?,password_hash=? WHERE id=1').bind(salt,hash).run();
  if(!result.meta?.changes)return Response.json({error:'لم يتم العثور على حساب المدير'},{status:503});
  await env.DB.prepare('DELETE FROM sessions').run();
  return Response.json({ok:true},{headers:{'Cache-Control':'no-store'}});
 }catch(e){console.error('PASSWORD_CHANGE_FAILED',e?.name,e?.message);return Response.json({error:'تعذر تغيير كلمة المرور',code:'PASSWORD_CHANGE',reason:e?.name||'UNKNOWN'},{status:500})}
}
