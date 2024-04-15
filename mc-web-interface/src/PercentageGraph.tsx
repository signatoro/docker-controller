import React, { useState, useEffect } from 'react';
import Chart from 'chart.js/auto';

interface CPUData {
  timestamp: string;
  percentage: number;
}

interface CPUGraphProps {
  endpoint: string;
  title: string;
}

const PercentageGraph: React.FC<CPUGraphProps> = ({ endpoint, title }) => {
  const [cpuData, setCpuData] = useState<CPUData[]>([]);
  const canvasRef = React.useRef<HTMLCanvasElement>(null); // Ref to store canvas element

  useEffect(() => {
    fetchDataFromAPI();
  }, [endpoint]); // Run fetchDataFromAPI whenever endpoint changes

  const fetchDataFromAPI = async () => {
    try {
      const response = await fetch(endpoint);
      const responseData = await response.json();
      setCpuData(responseData);
    } catch (error) {
      console.error(`Error fetching CPU data from ${endpoint}:`, error);
    }
  };

  useEffect(() => {
    if (cpuData.length > 0) {
      renderChart();
    }
  }, [cpuData]); // Run renderChart whenever cpuData changes

  const renderChart = () => {
    const ctx = canvasRef.current;
    if (!ctx) return;

    // Destroy the previous Chart instance if it exists
    Chart.getChart(ctx)?.destroy();

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: cpuData.map(data => data.timestamp),
        datasets: [
          {
            label: 'CPU Percentage',
            data: cpuData.map(data => data.percentage),
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
          },
        ],
      },
    });
  };

  return (
    <div>
      <h2>{title}</h2>
      <canvas ref={canvasRef} width={600} height={400}></canvas>
    </div>
  );
};

export default PercentageGraph;
