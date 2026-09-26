import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// ينظف الـ DOM بعد كل تست عشان التستات ما تأثرش في بعض
afterEach(() => {
    cleanup();
});