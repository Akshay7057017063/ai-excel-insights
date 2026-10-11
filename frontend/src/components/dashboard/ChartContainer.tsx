import React from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import { ChartSpec } from '../../types'
import { BarChart3 } from 'lucide-react'

export interface ChartContainerProps {
  chart: ChartSpec
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

export const ChartContainer: React.FC<ChartContainerProps> = ({ chart }) => {
  const hasData = chart.data && chart.data.length > 0

  // Detect keys for series
  const dataKeys = hasData
    ? Object.keys(chart.data[0]).filter((key) => key !== chart.x_label && key !== 'name' && key !== 'id')
    : []

  const renderChart = () => {
    if (!hasData) {
      return (
        <div className="h-64 flex flex-col items-center justify-center text-gray-400">
          <BarChart3 className="w-8 h-8 mb-2 opacity-50" />
          <p className="text-sm">No data available for this chart</p>
        </div>
      )
    }

    const xKey = chart.x_label || Object.keys(chart.data[0])[0]

    switch (chart.type) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chart.data} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey={xKey} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
              <YAxis tick={{ fontSize: 12, fill: '#64748b' }} dx={-5} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.5rem',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  fontSize: '12px',
                }}
              />
              <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px' }} />
              {dataKeys.length > 0 ? (
                dataKeys.map((key, idx) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={COLORS[idx % COLORS.length]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    activeDot={{ r: 6 }}
                  />
                ))
              ) : (
                <Line
                  type="monotone"
                  dataKey={chart.y_label || 'value'}
                  stroke={COLORS[0]}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chart.data} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey={xKey} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
              <YAxis tick={{ fontSize: 12, fill: '#64748b' }} dx={-5} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.5rem',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  fontSize: '12px',
                }}
              />
              <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px' }} />
              {dataKeys.length > 0 ? (
                dataKeys.map((key, idx) => (
                  <Bar
                    key={key}
                    dataKey={key}
                    fill={COLORS[idx % COLORS.length]}
                    radius={[4, 4, 0, 0]}
                  />
                ))
              ) : (
                <Bar
                  dataKey={chart.y_label || 'value'}
                  fill={COLORS[0]}
                  radius={[4, 4, 0, 0]}
                />
              )}
            </BarChart>
          </ResponsiveContainer>
        )

      case 'histogram':
        return (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart
              data={chart.data}
              barCategoryGap={1}
              margin={{ top: 10, right: 30, left: 10, bottom: 25 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey={xKey} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
              <YAxis tick={{ fontSize: 12, fill: '#64748b' }} dx={-5} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
              />
              <Bar
                dataKey={chart.y_label || dataKeys[0] || 'count'}
                fill={COLORS[0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'pie':
        const nameKey = xKey
        const valKey = chart.y_label || dataKeys[0] || 'value'
        return (
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
              />
              <Legend verticalAlign="bottom" wrapperStyle={{ fontSize: '12px' }} />
              <Pie
                data={chart.data}
                dataKey={valKey}
                nameKey={nameKey}
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {chart.data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        )

      case 'scatter':
        const yKey = chart.y_label || dataKeys[0] || 'y'
        return (
          <ResponsiveContainer width="100%" height={320}>
            <ScatterChart margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey={xKey}
                name={chart.x_label}
                tick={{ fontSize: 12, fill: '#64748b' }}
                dy={10}
              />
              <YAxis
                dataKey={yKey}
                name={chart.y_label}
                tick={{ fontSize: 12, fill: '#64748b' }}
                dx={-5}
              />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
              />
              <Scatter name={chart.title} data={chart.data} fill={COLORS[0]} />
            </ScatterChart>
          </ResponsiveContainer>
        )

      default:
        return null
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200/80 p-5 shadow-sm">
      <div className="mb-4">
        <h4 className="text-base font-semibold text-gray-900">{chart.title}</h4>
        {chart.description && (
          <p className="text-xs text-gray-500 mt-1">{chart.description}</p>
        )}
      </div>
      <div className="w-full">{renderChart()}</div>
    </div>
  )
}

export default ChartContainer
