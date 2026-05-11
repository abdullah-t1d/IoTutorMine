<template>
  <main class="auth-page">
    <div class="auth-card">
      <h1 class="auth-card__title">Login</h1>
      <p class="auth-card__subtitle">Sign in to your IoTutorMine account</p>

      <form @submit.prevent class="auth-form">
        <div class="auth-form__group">
          <label for="login-email" class="auth-form__label">Email</label>
          <input id="login-email" type="email" class="auth-form__input" placeholder="you@example.com" />
        </div>

        <div class="auth-form__group">
          <label for="login-password" class="auth-form__label">Password</label>
          <input id="login-password" type="password" class="auth-form__input" placeholder="••••••••" />
        </div>

        <button type="submit" class="auth-form__submit">Login</button>
      </form>

      <p class="auth-card__footer">
        Don't have an account? <router-link to="/register">Register</router-link>
      </p>
    </div>
  </main>
</template>

<style scoped>
.auth-page {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-xl) var(--space-xl) var(--space-lg);
}

.auth-card__title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  margin-bottom: var(--space-xs);
}

.auth-card__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-xl);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.auth-form__group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.auth-form__label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.auth-form__input {
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  outline: none;
  transition: border-color 0.15s;
}

.auth-form__input:focus {
  border-color: var(--color-accent);
}

.auth-form__submit {
  margin-top: var(--space-sm);
  padding: 11px 20px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: #fff;
  background: var(--color-accent);
  border: none;
  border-radius: var(--radius-sm);
  transition: background 0.15s;
}

.auth-form__submit:hover {
  background: var(--color-accent-hover);
}

.auth-card__footer {
  text-align: center;
  margin-top: var(--space-lg);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}
</style>
