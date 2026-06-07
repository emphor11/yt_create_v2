import { AppShell } from "./components/AppShell";
import { ProjectListPage } from "./pages/ProjectListPage";
import "./styles/global.css";

export function App() {
  return (
    <AppShell>
      <ProjectListPage />
    </AppShell>
  );
}
