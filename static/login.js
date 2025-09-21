(function() {
  // DOM 요소들
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const loginBtn = document.getElementById('login-btn');

  // 유효성 검사 함수들
  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function showError(input, message) {
    const formGroup = input.closest('.form-group');
    formGroup.classList.add('error');
    
    let errorElement = formGroup.querySelector('.error-message');
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.className = 'error-message';
      formGroup.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    errorElement.classList.add('show');
  }

  function clearError(input) {
    const formGroup = input.closest('.form-group');
    formGroup.classList.remove('error');
    
    const errorElement = formGroup.querySelector('.error-message');
    if (errorElement) {
      errorElement.classList.remove('show');
    }
  }

  function showSuccess(message) {
    let successElement = document.querySelector('.success-message');
    if (!successElement) {
      successElement = document.createElement('div');
      successElement.className = 'success-message';
      loginForm.insertBefore(successElement, loginForm.firstChild);
    }
    
    successElement.textContent = message;
    successElement.classList.add('show');
    
    // 3초 후 성공 메시지 숨기기
    setTimeout(() => {
      successElement.classList.remove('show');
    }, 3000);
  }

  function setLoading(isLoading) {
    loginBtn.disabled = isLoading;
    loginBtn.textContent = isLoading ? '로그인 중...' : '로그인';
  }

  // 실시간 유효성 검사
  emailInput.addEventListener('blur', () => {
    const email = emailInput.value.trim();
    if (email && !validateEmail(email)) {
      showError(emailInput, '올바른 이메일 형식을 입력해주세요.');
    } else {
      clearError(emailInput);
    }
  });

  // 입력 시 에러 메시지 제거
  [emailInput, passwordInput].forEach(input => {
    input.addEventListener('input', () => {
      clearError(input);
    });
  });

  // 버튼 클릭 처리
  loginBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    
    // 모든 에러 메시지 제거
    document.querySelectorAll('.error-message').forEach(el => el.classList.remove('show'));
    document.querySelectorAll('.form-group').forEach(el => el.classList.remove('error'));
    
    // 입력값 가져오기
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    
    // 유효성 검사
    let isValid = true;
    
    if (!email) {
      showError(emailInput, '이메일을 입력해주세요.');
      isValid = false;
    } else if (!validateEmail(email)) {
      showError(emailInput, '올바른 이메일 형식을 입력해주세요.');
      isValid = false;
    }
    
    if (!password) {
      showError(passwordInput, '비밀번호를 입력해주세요.');
      isValid = false;
    }
    
    if (!isValid) {
      return;
    }
    
    // API 연결 준비
    setLoading(true);
    
    try {
      // 실제 API 호출
      const loginData = {
        email: email,
        password: password
      };
      
      console.log('로그인 데이터:', loginData);
      
      const response = await fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData)
      });
      
      const result = await response.json();
      
      console.log('로그인 응답:', result);
      console.log('응답 상태:', response.status);
      
      if (response.ok) {
        // 성공 처리
        console.log('로그인 성공!');
        
        // 토큰을 localStorage에 저장
        localStorage.setItem('token', result.token);
        
        // 메인 페이지로 리다이렉트 (즉시)
        console.log('메인 페이지로 리다이렉트 중...');
        window.location.href = '/main';
      } else {
        // 에러 처리
        console.error('로그인 실패:', result);
        showError(emailInput, result.message || '로그인 중 오류가 발생했습니다.');
      }
      
    } catch (error) {
      console.error('로그인 오류:', error);
      showError(emailInput, '로그인 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  });

})();
