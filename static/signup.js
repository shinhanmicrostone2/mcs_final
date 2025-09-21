(function() {
  // DOM 요소들
  const signupForm = document.getElementById('signup-form');
  const emailInput = document.getElementById('email');
  const nameInput = document.getElementById('name');
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirm-password');
  const signupBtn = document.querySelector('.signup-btn');

  // 유효성 검사 함수들
  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function validatePassword(password) {
    // 최소 6자 이상 (더 간단한 규칙)
    return password.length >= 6;
  }

  function validateName(name) {
    return name.trim().length >= 2;
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
      signupForm.insertBefore(successElement, signupForm.firstChild);
    }
    
    successElement.textContent = message;
    successElement.classList.add('show');
    
    // 3초 후 성공 메시지 숨기기
    setTimeout(() => {
      successElement.classList.remove('show');
    }, 3000);
  }

  function setLoading(isLoading) {
    signupBtn.disabled = isLoading;
    signupBtn.textContent = isLoading ? '처리 중...' : '회원가입';
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

  nameInput.addEventListener('blur', () => {
    const name = nameInput.value.trim();
    if (name && !validateName(name)) {
      showError(nameInput, '이름은 2자 이상 입력해주세요.');
    } else {
      clearError(nameInput);
    }
  });

  passwordInput.addEventListener('blur', () => {
    const password = passwordInput.value;
    if (password && !validatePassword(password)) {
      showError(passwordInput, '비밀번호는 6자 이상 입력해주세요.');
    } else {
      clearError(passwordInput);
    }
  });

  confirmPasswordInput.addEventListener('blur', () => {
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    if (confirmPassword && password !== confirmPassword) {
      showError(confirmPasswordInput, '비밀번호가 일치하지 않습니다.');
    } else {
      clearError(confirmPasswordInput);
    }
  });

  // 입력 시 에러 메시지 제거
  [emailInput, nameInput, passwordInput, confirmPasswordInput].forEach(input => {
    input.addEventListener('input', () => {
      clearError(input);
    });
  });

  // 폼 제출 처리
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // 모든 에러 메시지 제거
    document.querySelectorAll('.error-message').forEach(el => el.classList.remove('show'));
    document.querySelectorAll('.form-group').forEach(el => el.classList.remove('error'));
    
    // 입력값 가져오기
    const email = emailInput.value.trim();
    const name = nameInput.value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    
    // 유효성 검사
    let isValid = true;
    
    if (!email) {
      showError(emailInput, '이메일을 입력해주세요.');
      isValid = false;
    } else if (!validateEmail(email)) {
      showError(emailInput, '올바른 이메일 형식을 입력해주세요.');
      isValid = false;
    }
    
    if (!name) {
      showError(nameInput, '이름을 입력해주세요.');
      isValid = false;
    } else if (!validateName(name)) {
      showError(nameInput, '이름은 2자 이상 입력해주세요.');
      isValid = false;
    }
    
    if (!password) {
      showError(passwordInput, '비밀번호를 입력해주세요.');
      isValid = false;
    } else if (!validatePassword(password)) {
      showError(passwordInput, '비밀번호는 6자 이상 입력해주세요.');
      isValid = false;
    }
    
    if (!confirmPassword) {
      showError(confirmPasswordInput, '비밀번호 확인을 입력해주세요.');
      isValid = false;
    } else if (password !== confirmPassword) {
      showError(confirmPasswordInput, '비밀번호가 일치하지 않습니다.');
      isValid = false;
    }
    
    if (!isValid) {
      return;
    }
    
    // API 연결 준비
    setLoading(true);
    
    try {
      // 실제 API 호출
      const signupData = {
        email: email,
        name: name,
        password: password
      };
      
      console.log('회원가입 데이터:', signupData);
      
      const response = await fetch('/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(signupData)
      });
      
      const result = await response.json();
      
      if (response.ok) {
        // 성공 처리
        showSuccess('회원가입이 완료되었습니다!');
        
        // 폼 초기화
        signupForm.reset();
        
        // 로그인 페이지로 리다이렉트
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
      } else {
        // 에러 처리
        showError(emailInput, result.message || '회원가입 중 오류가 발생했습니다.');
      }
      
    } catch (error) {
      console.error('회원가입 오류:', error);
      showError(emailInput, '회원가입 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  });

  // 실제 API 연결 시 사용할 함수 (주석 처리)
  /*
  async function signupUser(userData) {
    const response = await fetch('/api/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });
    
    if (!response.ok) {
      throw new Error('회원가입 실패');
    }
    
    return await response.json();
  }
  */

})();
