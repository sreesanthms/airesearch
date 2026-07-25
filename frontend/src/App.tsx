import { AppRouter } from './routes';
import { AppLayout } from './components/layout';

function App() {
  return (
    <AppLayout>
      <AppRouter />
    </AppLayout>
  );
}

export default App;
