import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import AssessmentDetail from './components/AssessmentDetail';
import ConnectionStatus from './components/ConnectionStatus'; // kept for page-level usage
import { AssessmentsProvider, useAssessments } from './context/AssessmentsContext';

const Shell: React.FC = () => {
  const { select } = useAssessments();
  const [view, setView] = useState<'dashboard' | 'assessment'>('dashboard');

  const openAssessment = async (id: string) => {
    await select(id);
    setView('assessment');
  };

  return (
    <div className="container">
      {view === 'dashboard' && <Dashboard onOpenAssessment={openAssessment} />}
      {view === 'assessment' && <AssessmentDetail onBack={() => setView('dashboard')} />}
    </div>
  );
};

const App: React.FC = () => (
  <AssessmentsProvider>
    <Shell />
  </AssessmentsProvider>
);

export default App;
