document.getElementById("searchTextBtn").addEventListener("click", async () => {
  const q = document.getElementById("textQuery").value.trim();
  if (!q) return alert("Enter a text query!");
  const fd = new FormData(); fd.append("query", q);
  const r = await fetch("/search/text_to_image",{method:"POST",body:fd});
  const d = await r.json();
  const c = document.getElementById("textResults");
  c.innerHTML="";
  d.forEach(x=>{
    c.innerHTML+=`<div class="col-md-3"><div class="card">
      <img src="${x.image_path}" class="result-img">
      <div class="card-body text-center"><p class="text-muted">Score: ${x.score}</p></div></div></div>`;
  });
});

document.getElementById("searchImageBtn").addEventListener("click", async () => {
  const f=document.getElementById("imageUpload").files[0];
  if(!f) return alert("Upload image!");
  const fd=new FormData();fd.append("file",f);
  const r=await fetch("/search/image_to_image",{method:"POST",body:fd});
  const d=await r.json();
  const c=document.getElementById("imageResults");c.innerHTML="";
  d.forEach(x=>{
    c.innerHTML+=`<div class="col-md-3"><div class="card">
      <img src="${x.image_path}" class="result-img">
      <div class="card-body text-center"><p class="text-muted">Score: ${x.score}</p></div></div></div>`;
  });
});

document.getElementById("searchCaptionBtn").addEventListener("click", async () => {
  const f=document.getElementById("captionUpload").files[0];
  if(!f) return alert("Upload image!");
  const fd=new FormData();fd.append("file",f);
  const r=await fetch("/search/image_to_text",{method:"POST",body:fd});
  const d=await r.json();
  const c=document.getElementById("captionResults");c.innerHTML="";
  d.forEach(x=>{c.innerHTML+=`<li class="list-group-item">${x.caption} (Score: ${x.score})</li>`});
});
