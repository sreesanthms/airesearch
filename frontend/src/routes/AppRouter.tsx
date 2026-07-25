import { Routes, Route } from 'react-router-dom';
import { HomePage } from '../pages/Home';
import { ChatPage } from '../pages/Chat';
import { NotFoundPage } from '../pages/NotFound';

export const AppRouter = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route path="/chat/:paperId" element={<ChatPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
