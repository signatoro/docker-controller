// DiskGraph.tsx
import React, { useState, useEffect } from 'react';
import Chart from 'chart.js/auto';

interface DiskData {
  timestamp: string;
  read: number;
  write: number;
}

interface DiskGraphProps {
  endpoint: string;
  title: string;
  width?: number;
  height?: number;
}

const DiskGraph: React.FC<DiskGraphProps> = ({ endpoint, title, width = 400, height = 200 }) => {
  const [diskData, setDiskData] = useState<DiskData[]>([]);
  const canvasRef = React.useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    fetchDataFromAPI();
  }, [endpoint]);

  const fetchDataFromAPI = async () => {
    try {
      const response = await fetch(endpoint);
      const responseData = await response.json();
      setDiskData(responseData);
    } catch (error) {
      console.error(`Error fetching disk data from ${endpoint}:`, error);
    }
  };

  useEffect(() => {
    if (diskData.length > 0) {
      renderChart();
    }
  }, [diskData]);

  const renderChart = () => {
    const ctx = canvasRef.current;
    if (!ctx) return;

    Chart.getChart(ctx)?.destroy();

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: diskData.map(data => data.timestamp),
        datasets: [
          {
            label: 'Read (MB)',
            data: diskData.map(data => bytesToMB(data.read)),
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
          },
          {
            label: 'Write (MB)',
            data: diskData.map(data => bytesToMB(data.write)),
            borderColor: 'rgb(192, 75, 192)',
            tension: 0.1,
          },
        ],
      },
    });
  };

  // Function to convert bytes to megabytes
  const bytesToMB = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2);
  };

  return (
    <div>
      <h2>{title}</h2>
      <canvas ref={canvasRef} width={600} height={400}></canvas>
    </div>
  );
};

export default DiskGraph;
