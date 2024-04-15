import React from 'react';
import PercentageGraph from './PercentageGraph';
import DiskGraph from './DiskGraph';
import { ThemeProvider, useTheme } from './ThemeContext';

const App: React.FC = () => {
  return (
    // <ThemeProvider>
    //   <ThemedApp />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gridGap: '20px', padding: '20px', height: '100vh' }}>
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <PercentageGraph endpoint='http://127.0.0.1:8000/cpu-data' title='CPU Data'/>
        </div>
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <PercentageGraph endpoint='http://127.0.0.1:8000/ram-data' title='Ram Data'/>
        </div>
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <DiskGraph endpoint='http://127.0.0.1:8000/net-data' title='Network Data'/>
        </div>
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <DiskGraph endpoint='http://127.0.0.1:8000/net-data' title='Block Data'/>
        </div>
      </div>
    // </ThemeProvider>
  );
};

const ThemedApp: React.FC = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <div style={{ background: isDarkMode ? '#222' : '#fff', color: isDarkMode ? '#fff' : '#333', minHeight: '100vh' }}>
      <h1>Hello World</h1>
      <button onClick={toggleTheme}>Toggle Dark Mode</button>
    </div>
  );
};

export default App;
