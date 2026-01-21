"use client"

import { Area, AreaChart, CartesianGrid, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts"

interface MoodAreaProps {
  data: {
    date: string;
    Mood: number | null;
  }[];
}

export function MoodArea({ data }: MoodAreaProps) {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{
            top: 20,
            right: 20,
            left: -20,
            bottom: 0,
          }}
        >
          <defs>
            <linearGradient id="colorMood" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#d946ef" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#d946ef" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="date" 
            tickLine={false} 
            axisLine={false} 
            tickMargin={10} 
            tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
          />
          <YAxis 
            domain={[0, 10]} 
            tickLine={false} 
            axisLine={false} 
            tickMargin={10} 
            tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
          />
          <Tooltip
             contentStyle={{ 
               backgroundColor: 'hsl(var(--card))', 
               borderColor: 'hsl(var(--border))', 
               color: 'hsl(var(--foreground))',
               borderRadius: 'var(--radius)',
             }}
             itemStyle={{ color: 'hsl(var(--foreground))' }}
             labelStyle={{ color: 'hsl(var(--muted-foreground))' }}
          />
          <Area 
            type="monotone" 
            dataKey="Mood" 
            stroke="#d946ef" 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorMood)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
