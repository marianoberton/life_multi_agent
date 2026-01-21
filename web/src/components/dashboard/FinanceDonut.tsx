"use client"

import * as React from "react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"

const currencyFormatter = (number: number) =>
  `$${Intl.NumberFormat('es-AR').format(number).toString()}`

interface FinanceDonutProps {
  data: {
    name: string;
    value: number;
  }[];
}

// Shadcn compatible colors (using CSS variables or Tailwind colors)
const COLORS = [
  "#f87171", // red-400
  "#fb923c", // orange-400
  "#fbbf24", // amber-400
  "#a3e635", // lime-400
  "#34d399", // emerald-400
  "#22d3ee", // cyan-400
  "#818cf8", // indigo-400
  "#c084fc", // violet-400
];

export function FinanceDonut({ data }: FinanceDonutProps) {
  const activeData = data.filter(item => item.value > 0);

  if (activeData.length === 0) {
     return <div className="text-center text-muted-foreground p-4">No hay datos</div>;
  }

  // Calculate total for the center text
  const total = activeData.reduce((acc, curr) => acc + curr.value, 0);

  return (
    <div className="h-[300px] w-full relative flex flex-col items-center">
      <div className="h-[200px] w-full relative">
        <ResponsiveContainer width="100%" height="100%">
            <PieChart>
            <Pie
                data={activeData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
            >
                {activeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
            </Pie>
            <Tooltip 
                formatter={(value: number) => currencyFormatter(value)}
                contentStyle={{ 
                backgroundColor: 'hsl(var(--card))', 
                borderColor: 'hsl(var(--border))', 
                color: 'hsl(var(--foreground))',
                borderRadius: 'var(--radius)',
                }}
                itemStyle={{ color: 'hsl(var(--foreground))' }}
            />
            </PieChart>
        </ResponsiveContainer>
        {/* Center Text */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center">
                <span className="text-xl font-bold text-foreground block">
                    {currencyFormatter(total)}
                </span>
                <span className="text-xs text-muted-foreground">Total</span>
            </div>
        </div>
      </div>
      
      <div className="flex flex-wrap justify-center gap-x-4 gap-y-2 mt-4">
        {activeData.map((entry, index) => (
            <div key={index} className="flex items-center gap-2 text-xs text-muted-foreground">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                <span>{entry.name}</span>
            </div>
        ))}
      </div>
    </div>
  )
}
