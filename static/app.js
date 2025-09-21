(function(){
  const LOGIN_REDIRECT_URL = 'https://example.com/login';  // 나중에 실제 로그인 URL로 교체
  const CHAT_ROUTE_PREFIX  = '#/chat/';
  const STORAGE_KEY        = 'lawgpt_conversations_v2';

  const chatWrap  = document.getElementById('chat');
  const composer  = document.getElementById('composer');
  const sendBtn   = document.getElementById('send-btn');
  const convList  = document.getElementById('conv-list');
  const newChat   = document.getElementById('new-chat');
  const logoutBtn = document.querySelector('.logout');
  const lawRail   = document.getElementById('law-rail');

  // ✅ 슬라이드 사이드바 관련
  const sidebar   = document.getElementById('sidebar');
  const scrim     = document.getElementById('scrim');
  const burgerBtn = document.getElementById('sidebar-toggle');

  function isMobile(){ return window.innerWidth <= 1024; }
  function openSidebar(){
    if(!isMobile()) return;
    sidebar.classList.add('open');
    scrim.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function closeSidebar(){
    sidebar.classList.remove('open');
    scrim.classList.remove('show');
    document.body.style.overflow = '';
  }
  burgerBtn.addEventListener('click', openSidebar);
  scrim.addEventListener('click', closeSidebar);
  window.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeSidebar(); });
  window.addEventListener('resize', ()=>{
    if(!isMobile()) closeSidebar();
  });

  /* ======== 질문 키워드 → 법률 링크 ======== */
  const LAW_DB = [
    { keys:['무죄추정','무죄 추정','유죄'], bullets:[
      { text:'무죄추정의 원칙 (헌법 제27조)', url:q('무죄추정 헌법 27조') },
      { text:'무죄추정 관련 판례',               url:q('무죄추정 판례') }
    ]},
    { keys:['자백배제','자백 배제','자백'], bullets:[
      { text:'자백배제법칙 개요',               url:q('자백배제법칙') },
      { text:'자백의 보강법칙(형사소송법)',       url:q('자백 보강법칙 형사소송법') }
    ]},
    { keys:['친고죄','고소','고소장'], bullets:[
      { text:'친고죄의 의의와 요건',             url:q('친고죄 요건') },
      { text:'친고죄 관련 판례',                 url:q('친고죄 판례') }
    ]},
    { keys:['살인'], bullets:[
      { text:'살인죄: 형법 제250조',            url:q('형법 250조 살인') },
      { text:'살인죄 판례',                      url:q('살인죄 판례') }
    ]},
    { keys:['절도'], bullets:[
      { text:'절도죄: 형법 제329조',             url:q('형법 329조 절도') },
      { text:'절도죄 판례',                      url:q('절도죄 판례') }
    ]},
    { keys:['사기'], bullets:[
      { text:'사기죄: 형법 제347조',             url:q('형법 347조 사기') },
      { text:'사기죄 판례',                      url:q('사기죄 판례') }
    ]},
    { keys:['형사소송법','수사','기소','재판','집행','변호인','증거','적법절차'], bullets:[
      { text:'형사소송법 총론',                  url:q('형사소송법') },
      { text:'증거능력/증거조사',                 url:q('형사소송법 증거능력') }
    ]},
    { keys:['형법','범죄','책임','양형'], bullets:[
      { text:'형법 총론',                        url:q('형법 총론') },
      { text:'양형 기준(대법원 양형위원회)',       url:q('양형 기준') }
    ]},
  ];
  function q(keyword){
    return 'https://www.law.go.kr/LSW/precSc.do?query=' + encodeURIComponent(keyword);
  }
  function findRelatedLaws(text=''){
    const t = text.toLowerCase();
    const found = [];
    LAW_DB.forEach(entry=>{
      if(entry.keys.some(k => t.includes(k.toLowerCase()))) found.push(entry);
    });
    if(found.length===0){
      found.push({ bullets:[
        {text:'형법 총론', url:q('형법 총론')},
        {text:'형사소송법 총론', url:q('형사소송법 총론')}
      ]});
    }
    return found;
  }
  function renderLawLinks(groups){
    if(!lawRail) return;
    const html = [
      '<h3>법률 링크</h3>',
      ...groups.map(g=>{
        const items = (g.bullets||[]).map(b=>
          `<li><a class="rule-link" href="${b.url}" target="_blank" rel="noopener">${escapeHtml(b.text)}</a></li>`
        ).join('');
        return `<div class="rule"><ul>${items}</ul></div>`;
      })
    ].join('');
    lawRail.innerHTML = html;
  }
  renderLawLinks([]);

  /* ======== 상태 ======== */
  let conversations = [];
  let activeId = null;
  // 현재 사용자 ID 가져오기 (JWT 토큰에서)
  function getCurrentUserId() {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    try {
      // JWT 토큰 디코딩 (간단한 방법)
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.user_id || payload.id;
    } catch (error) {
      console.error('토큰 디코딩 실패:', error);
      return null;
    }
  }
  
  const CURRENT_USER_ID = getCurrentUserId();
  
  // 메인 페이지에서만 사용자 ID 체크 (로그인 페이지에서는 체크하지 않음)
  if (window.location.pathname === '/main' && !CURRENT_USER_ID) {
    console.log('사용자 ID가 없습니다. 로그인 페이지로 이동합니다.');
    window.location.href = '/';
    return;
  }

  /* ======== 유틸 ======== */
  const uid = () => (crypto?.randomUUID?.() || Math.random().toString(36).slice(2));
  const now = () => Date.now();
  
  // 데이터베이스 기반 채팅방 로드
  async function loadChatRoomsFromDB() {
    const userId = getCurrentUserId();
    if (!userId) {
      console.error('사용자 ID가 없어서 채팅방을 로드할 수 없습니다.');
      return false;
    }
    
    try {
      const response = await fetch(`/api/chatrooms/user/${userId}`);
      if (response.ok) {
        const data = await response.json();
        conversations = [];
        
        // 각 채팅방의 메시지도 함께 로드
        for (const room of data.chatrooms) {
          const messages = await loadChatMessagesFromDB(room.id);
          conversations.push({
            id: room.id.toString(),
            title: room.title,
            updatedAt: new Date(room.created_at).getTime(),
            messages: messages
          });
        }
        
        if (conversations.length > 0) {
          activeId = conversations[0].id;
        }
        return true;
      } else {
        console.error('채팅방 로드 실패:', response.status, await response.text());
      }
    } catch (error) {
      console.error('채팅방 로드 실패:', error);
    }
    return false;
  }

  // 데이터베이스에서 채팅 메시지 로드
  async function loadChatMessagesFromDB(chatRoomId) {
    try {
      const response = await fetch(`/chat/messages/${chatRoomId}`);
      if (response.ok) {
        const messages = await response.json();
        const formattedMessages = [];
        
        // 질문과 답변을 순서대로 정렬
        messages.forEach(msg => {
          formattedMessages.push({
            role: 'user',
            content: msg.question,
            ts: new Date(msg.created_at).getTime()
          });
          formattedMessages.push({
            role: 'assistant',
            content: msg.response,
            ts: new Date(msg.created_at).getTime() + 1 // 응답이 질문보다 1ms 늦게 표시
          });
        });
        
        return formattedMessages.sort((a, b) => a.ts - b.ts);
      }
    } catch (error) {
      console.error('채팅 메시지 로드 실패:', error);
    }
    return [];
  }

  // 데이터베이스에 채팅방 저장
  async function saveChatRoomToDB(title) {
    const userId = getCurrentUserId();
    if (!userId) {
      console.error('사용자 ID가 없어서 채팅방을 저장할 수 없습니다.');
      return null;
    }
    
    try {
      const response = await fetch('/api/chatrooms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          title: title
        })
      });
      if (response.ok) {
        const data = await response.json();
        return data.room_id.toString();
      } else {
        console.error('채팅방 저장 실패:', response.status, await response.text());
      }
    } catch (error) {
      console.error('채팅방 저장 실패:', error);
    }
    return null;
  }

  // 데이터베이스에 채팅 메시지 저장
  async function saveChatMessageToDB(chatRoomId, question, aiResponse) {
    const userId = getCurrentUserId();
    console.log('=== 채팅 메시지 저장 시도 ===');
    console.log('사용자 ID:', userId);
    console.log('채팅방 ID:', chatRoomId);
    console.log('질문:', question);
    console.log('응답:', aiResponse);
    
    if (!userId) {
      console.error('사용자 ID가 없어서 메시지를 저장할 수 없습니다.');
      return;
    }
    
    try {
      const requestData = {
        user_id: userId,
        chat_room_id: parseInt(chatRoomId),
        question: question,
        response: aiResponse
      };
      
      console.log('전송할 데이터:', requestData);
      
      const fetchResponse = await fetch('/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });
      
      console.log('응답 상태:', fetchResponse.status);
      const responseText = await fetchResponse.text();
      console.log('응답 내용:', responseText);
      
      if (fetchResponse.ok) {
        console.log('✅ 채팅 메시지가 데이터베이스에 저장되었습니다.');
      } else {
        console.error('❌ 채팅 메시지 저장 실패:', fetchResponse.status, responseText);
      }
    } catch (error) {
      console.error('❌ 채팅 메시지 저장 오류:', error);
    }
  }

  // 기존 로컬 스토리지 함수들 (호환성을 위해 유지)
  const saveState = () => localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
  function loadState(){ try{ return JSON.parse(localStorage.getItem(STORAGE_KEY)||'[]'); }catch(e){ return []; } }
  function escapeHtml(s=''){ return s.replace(/[&<>"']/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }
  function snippet(s='', n=40){ const t=s.replace(/\s+/g,' ').trim(); return t.length>n?t.slice(0,n)+'…':t; }
  function looksLikeSample(conv){
    const txt = (conv.messages||[]).map(m=>m.content||'').join('\n');
    return /형사소송법|친고죄원칙|자백배제법칙|설명\s*\n/i.test(txt);
  }
  function purgeSampleData(convs){
    if(!Array.isArray(convs) || convs.length===0) return [];
    const filtered = convs.filter(c=>!looksLikeSample(c));
    return filtered.length ? filtered : [];
  }

  // 초기화: 데이터베이스에서 채팅방 로드
  async function initializeApp() {
    const success = await loadChatRoomsFromDB();
    if (!success || conversations.length === 0) {
      // 데이터베이스 로드 실패 또는 채팅방이 없으면 새로 생성
      const roomId = await saveChatRoomToDB('새 대화');
      if (roomId) {
        const conv = { id: roomId, title: '새 대화', updatedAt: now(), messages: [] };
        conversations.push(conv); 
        activeId = roomId;
      } else {
        // 데이터베이스 저장 실패 시 로컬 스토리지 사용
        const conv = { id: uid(), title: '새 대화', updatedAt: now(), messages: [] };
        conversations.push(conv); 
        activeId = conv.id; 
        saveState();
      }
    }
    renderConvList();
    if (!location.hash) {
      if (!activeId) {
        await createNewConversationAndGo();
      } else {
        location.replace(CHAT_ROUTE_PREFIX + activeId);
      }
    }
    routeFromHash();
  }

  /* ======== 렌더: 좌측 대화 목록 ======== */
  function renderConvList(){
    const items = [...conversations].sort((a,b)=>b.updatedAt - a.updatedAt);
    convList.innerHTML = items.map(c=>{
      const last = c.messages[c.messages.length-1]?.content || '';
      return `
        <div class="row ${c.id===activeId?'active':''}" data-id="${c.id}">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.6">
            <path d="M21 12a8 8 0 0 1-8 8H7l-4 3v-6a8 8 0 1 1 18-5z" opacity=".8"/>
          </svg>
          <div class="textcol">
            <div class="title">${escapeHtml(c.title || '제목 없음')}</div>
            <div class="preview">${escapeHtml(snippet(last))}</div>
          </div>
          <a href="#" class="kebab-link" title="더보기" aria-label="더보기">⋯</a>
        </div>
      `;
    }).join('');
  }

  /* ======== 렌더: 중앙 채팅 ======== */
  function renderChat(){
    const conv = conversations.find(c=>c.id===activeId);
    if(!conv) return;
    chatWrap.innerHTML = '';
    conv.messages.forEach(m=>{
      if(m.role==='user'){
        const el = document.createElement('div');
        el.className = 'msg user';
        el.textContent = m.content;
        chatWrap.appendChild(el);
      }else{
        const row = document.createElement('div');
        row.className = 'ai-row';
        row.innerHTML = `
          <div class="avatar">A</div>
          <div class="msg ai">
            <div class="ai-content"></div>
            <div class="quick-in">
              <span class="link-like">엑셀파일로 저장</span>
              <span class="link-like">텍스트로저장</span>
              <span class="emoji">👍</span>
              <span class="emoji">👎</span>
            </div>
          </div>
        `;
        row.querySelector('.ai-content').innerHTML = m.content.replace(/\n/g,'<br>');
        chatWrap.appendChild(row);
      }
    });
    const actions = document.createElement('div');
    actions.className = 'chat-actions';
    actions.innerHTML = `
      <button class="btn primary">고소장 작성하기</button>
      <button class="btn primary">진술서 작성하기</button>
    `;
    chatWrap.appendChild(actions);
    chatWrap.scrollTop = chatWrap.scrollHeight;
  }

  /* ======== New Chat ======== */
  async function createNewConversationAndGo(){
    const roomId = await saveChatRoomToDB('새 대화');
    if (roomId) {
      const conv = { id: roomId, title: '새 대화', updatedAt: now(), messages: [] };
      conversations.unshift(conv);
      activeId = roomId;
      saveState();
      renderConvList();
      renderChat();
    } else {
      console.error('새 채팅방 생성에 실패했습니다.');
    }
  }

  /* ======== 라우터 ======== */
  function routeFromHash(){
    const h = location.hash || '';
    if(h.startsWith(CHAT_ROUTE_PREFIX)){
      const id = h.slice(CHAT_ROUTE_PREFIX.length);
      if(id === 'new'){ createNewConversationAndGo(); return; }
      const exists = conversations.find(c=>c.id===id);
      if(exists){ activeId = id; renderConvList(); renderChat(); closeSidebar(); return; } // 모바일에서 전환 시 자동 닫기
    }
    if(activeId) location.replace(CHAT_ROUTE_PREFIX + activeId);
  }
  window.addEventListener('hashchange', routeFromHash);

  /* ======== 입력창 자동 높이 ======== */
  function autoResize(el){ el.style.height='auto'; el.style.height = el.scrollHeight+'px'; }
  if(composer){
    ['input','change'].forEach(e=>composer.addEventListener(e, ()=>autoResize(composer)));
    window.addEventListener('load', ()=>autoResize(composer));
  }

  /* ======== 전송 ======== */
  async function onSend(){
    const text = composer.value.trim();
    if(!text) return;

    if(!activeId){ createNewConversationAndGo(); return; }
    const conv = conversations.find(c=>c.id===activeId);
    if(!conv) return;

    // 첫 문장 = 제목
    if(!conv.title || conv.title==='새 대화') {
      conv.title = text;
      // 데이터베이스에서 제목 업데이트
      try {
        const response = await fetch(`/api/chatrooms/${conv.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: text })
        });
        if (response.ok) {
          console.log('채팅방 제목이 데이터베이스에서 업데이트되었습니다.');
        }
      } catch (error) {
        console.error('제목 업데이트 중 오류:', error);
      }
    }

    // 사용자 메시지
    conv.messages.push({ role:'user', content:text, ts:now() });
    conv.updatedAt = now();
    composer.value = ''; autoResize(composer);

    // 자리표시 assistant
    conv.messages.push({ role:'assistant', content:'응답을 생성 중입니다…', ts:now() });
    saveState();
    renderConvList(); renderChat();

    // 실제 AI API 호출
    let aiText = '오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    let modelAvailable = true;
    try{
      const res = await fetch('/api/chat', {
        method:'POST',
        headers:{ 'Content-Type':'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      if(res.ok){
        aiText = data.answer || aiText;
        modelAvailable = data.model_available !== false;
      }else{
        aiText = data.error || aiText;
      }
    }catch(err){
      console.error(err);
    }

    // 모델이 사용 불가능한 경우 사용자에게 알림
    if (!modelAvailable) {
      aiText = "⚠️ AI 모델이 현재 사용할 수 없습니다.\n\n" + aiText + "\n\n💡 해결 방법:\n• ai_models 디렉토리가 있는지 확인해주세요\n• 필요한 모델 파일들이 모두 있는지 확인해주세요\n• 서버를 재시작해보세요";
    }

    const lastIdx = conv.messages.length - 1;
    if(conv.messages[lastIdx]?.role==='assistant'){
      conv.messages[lastIdx].content = aiText;
      conv.messages[lastIdx].ts = now();
    }else{
      conv.messages.push({ role:'assistant', content: aiText, ts: now() });
    }
    conv.updatedAt = now();
    
    // 데이터베이스에 채팅 메시지 저장
    await saveChatMessageToDB(conv.id, text, aiText);
    
    saveState();
    renderConvList(); renderChat();

    // 🔗 질문 기반으로 우측 법률 링크 갱신
    const groups = findRelatedLaws(text);
    renderLawLinks(groups);
  }

  sendBtn.addEventListener('click', onSend);
  composer.addEventListener('keydown', (e)=>{
    if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); onSend(); }
  });

  /* ======== 좌측 목록: 케밥 메뉴(삭제) ======== */
  let kebabMenu = null;
  function ensureKebabMenu(){
    if(kebabMenu) return kebabMenu;
    kebabMenu = document.createElement('div');
    kebabMenu.className = 'kebab-menu';
    kebabMenu.innerHTML = `<button class="kebab-item" data-action="delete">삭제</button>`;
    document.body.appendChild(kebabMenu);
    kebabMenu.addEventListener('click', (e)=>{
      const btn = e.target.closest('.kebab-item');
      if(!btn) return;
      const id = kebabMenu.dataset.id;
      if(btn.dataset.action==='delete' && id){
        deleteConversation(id);
        closeKebabMenu();
      }
    });
    return kebabMenu;
  }
  function openKebabMenu(anchorEl, convId){
    const menu = ensureKebabMenu();
    const r = anchorEl.getBoundingClientRect();
    menu.style.left = (r.right - 96) + 'px';
    menu.style.top  = (r.bottom + 6) + 'px';
    menu.dataset.id = convId;
    menu.style.display = 'block';
  }
  function closeKebabMenu(){ if(kebabMenu) kebabMenu.style.display='none'; }
  document.addEventListener('click', (e)=>{
    if(e.target.closest('.kebab-menu')) return;
    if(e.target.closest('.kebab-link')) return;
    closeKebabMenu();
  });
  window.addEventListener('scroll', closeKebabMenu, true);
  window.addEventListener('resize', closeKebabMenu);

  async function deleteConversation(id){
    const idx = conversations.findIndex(c=>c.id===id);
    if(idx<0) return;
    const deletingActive = (conversations[idx].id === activeId);
    
    // 데이터베이스에서 채팅방 삭제
    try {
      const response = await fetch(`/api/chatrooms/${id}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        console.log('채팅방이 데이터베이스에서 삭제되었습니다.');
      } else {
        console.error('데이터베이스 삭제 실패:', response.status);
      }
    } catch (error) {
      console.error('채팅방 삭제 중 오류:', error);
    }
    
    // 로컬 상태에서도 삭제
    conversations.splice(idx,1);
    saveState();

    if(conversations.length===0){
      createNewConversationAndGo();
    }else if(deletingActive){
      const nextId = [...conversations].sort((a,b)=>b.updatedAt-a.updatedAt)[0].id;
      location.hash = CHAT_ROUTE_PREFIX + nextId;
    }else{
      renderConvList();
    }
  }

  // 리스트 클릭: 행 선택 or 케밥 메뉴 열기
  convList.addEventListener('click', (e)=>{
    const kebab = e.target.closest('.kebab-link');
    if(kebab){
      e.preventDefault();
      const row = kebab.closest('.row');
      if(!row) return;
      openKebabMenu(kebab, row.dataset.id);
      return;
    }
    const row = e.target.closest('.row');
    if(!row) return;
    closeKebabMenu();
    location.hash = CHAT_ROUTE_PREFIX + row.dataset.id;
    closeSidebar(); // 모바일에서 목록 항목 클릭 시 자동 닫기
  });

  // New Chat → 새 대화
  newChat.addEventListener('click', ()=>{
    location.hash = CHAT_ROUTE_PREFIX + 'new';
    closeSidebar();
  });

 // 채팅 말풍선 내부 퀵액션(👍/👎/저장) — 토글 & 상호배타
  chatWrap.addEventListener('click', (e)=>{
  const t = e.target;

  if (t.classList.contains('emoji')) {
    const wrap = t.closest('.quick-in'); 
    if (!wrap) return;

    const isActive = t.classList.contains('active');
    if (isActive) {
      // 같은 이모지를 다시 누르면 해제
      t.classList.remove('active');
    } else {
      // 켤 때는 반대쪽 해제하고 이쪽만 활성화
      wrap.querySelectorAll('.emoji').forEach(x => x.classList.remove('active'));
      t.classList.add('active');
    }
    return;
  }

  if (t.classList.contains('link-like')) {
    e.preventDefault();
    console.log('action:', t.textContent.trim());
  }
});


  // 로그아웃 → 로그인 페이지로 이동
  logoutBtn.addEventListener('click', ()=>{
    window.location.href = LOGIN_REDIRECT_URL;
  });

  // 초기 렌더 & 라우팅
  initializeApp();
})();
