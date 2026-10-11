import React from 'react'
import { KPICard } from '../../types'
import { TrendingUp, TrendingDown, Minus, Activity, DollarSign, Users, ShoppingCart, Percent, BarChart2 } from 'lucide-react'

export interface KPICardComponentProps {
  card: KPICard
}

export const KPICardComponent: React.FC<KPICardComponentProps> = ({ card }) => {
  const getIcon = () => {
    const titleLower = card.title.toLowerCase()
    if (titleLower.includes('revenue') || titleLower.includes('sale') || titleLower.includes('profit') || titleLower.includes('cost')) {
      return <DollarSign className="w-5 h-5 text-blue-600" />
    }
    if (titleLower.includes('user') || titleLower.includes('customer') || titleLower.includes('client')) {
      return <Users className="w-5 h-5 text-indigo-600" />
    }
    if (titleLower.includes('order') || titleLower.includes('quantity') || titleLower.includes('item')) {
      return <ShoppingCart className="w-5 h-5 text-emerald-600" />
    }
    if (titleLower.includes('rate') || titleLower.includes('margin') || titleLower.includes('%')) {
      return <Percent className="w-5 h-5 text-purple-600" />
    }
    if (card.icon === 'activity') return <Activity className="w-5 h-5 text-blue-600" />
    return <BarChart2 className="w-5 h-5 text-blue-600" />
  }

  const isPositive = card.change_direction === 'up'
  const isNegative = card.change_direction === 'down'

  return (
    <div className="bg-white rounded-xl border border-gray-200/80 p-5 shadow-sm hover:shadow transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          {card.title}
        </span>
        <div className="w-9 h-9 rounded-lg bg-gray-50 flex items-center justify-center border border-gray-100">
          {getIcon()}
        </div>
      </div>

      <div className="flex items-baseline gap-2 mb-2">
        <span className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">
          {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
        </span>
        {card.unit && <span className="text-sm font-medium text-gray-500">{card.unit}</span>}
      </div>

      <div className="flex items-center justify-between text-xs pt-1">
        {card.change_pct !== undefined ? (
          <div
            className={`flex items-center font-medium ${
              isPositive
                ? 'text-emerald-600'
                : isNegative
                ? 'text-rose-600'
                : 'text-gray-500'
            }`}
          >
            {isPositive && <TrendingUp className="w-3.5 h-3.5 mr-1" />}
            {isNegative && <TrendingDown className="w-3.5 h-3.5 mr-1" />}
            {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5 mr-1" />}
            <span>
              {card.change_pct > 0 ? `+${card.change_pct.toFixed(1)}%` : `${card.change_pct.toFixed(1)}%`}
            </span>
          </div>
        ) : (
          <span className="text-gray-400">Current</span>
        )}

        <span className="text-gray-500 truncate max-w-[60%] text-right" title={card.description}>
          {card.description}
        </span>
      </div>
    </div>
  )
}

export default KPICardComponent
