import { AppShell } from "./components/AppShell";
import { HomePage } from "./pages/HomePage";
import "./styles/global.css";

export function App() {
  return (
    <AppShell>
      <HomePage />
    </AppShell>
  );
}

