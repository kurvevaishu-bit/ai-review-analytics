import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function TopicsChart({ topics }) {
  if (!topics || topics.length === 0) {
    return <p style={{ color: "#888" }}>No topic data yet (AI topic extraction needs API credits).</p>;
  }
  const data = topics.map(([name, count]) => ({ name, count }));
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <XAxis type="number" allowDecimals={false} />
        <YAxis dataKey="name" type="category" width={140} />
        <Tooltip />
        <Bar dataKey="count" fill="#3b82f6" />
      </BarChart>
    </ResponsiveContainer>
  );
}
