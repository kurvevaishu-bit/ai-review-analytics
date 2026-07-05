import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = { positive: "#22c55e", negative: "#ef4444", neutral: "#94a3b8" };

export default function SentimentChart({ data, title }) {
  const chartData = Object.entries(data).map(([name, value]) => ({ name, value }));
  return (
    <div style={{ flex: 1, minWidth: 280 }}>
      <h4 style={{ textAlign: "center" }}>{title}</h4>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" outerRadius={90} label>
            {chartData.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name] || "#ccc"} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
