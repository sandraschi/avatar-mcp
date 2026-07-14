import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Control } from '@/pages/control';
import { Tools } from '@/pages/tools';
import { Registry } from '@/pages/registry';
import { Unity } from '@/pages/unity';
import { VRChat } from '@/pages/vrchat';
import { Visualizer } from '@/pages/visualizer';
import { Chat } from '@/pages/chat';
import { Settings } from '@/pages/settings';
import { Animation } from '@/pages/animation';
import { Emotion } from '@/pages/emotion';
import { Audio } from '@/pages/audio';
import { Intelligence } from '@/pages/intelligence';
import { Artifacts } from '@/pages/artifacts';
import { Loops } from '@/pages/loops';
import { Status } from '@/pages/status';
import { Apps } from '@/pages/apps';
import { Help } from '@/pages/help';
import { Workflow } from '@/pages/workflow';
import { Pipeline } from '@/pages/pipeline';
import Logging from '@/pages/Logging';

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/control" element={<Control />} />
          <Route path="/animation" element={<Animation />} />
          <Route path="/emotion" element={<Emotion />} />
          <Route path="/audio" element={<Audio />} />
          <Route path="/registry" element={<Registry />} />
          <Route path="/unity" element={<Unity />} />
          <Route path="/vrchat" element={<VRChat />} />
          <Route path="/visualizer" element={<Visualizer />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/intelligence" element={<Intelligence />} />
          <Route path="/artifacts" element={<Artifacts />} />
          <Route path="/loops" element={<Loops />} />
          <Route path="/status" element={<Status />} />
          <Route path="/apps" element={<Apps />} />
          <Route path="/workflow" element={<Workflow />} />
          <Route path="/pipeline" element={<Pipeline />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/logging" element={<Logging />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
