import React from 'react'
import { InsightCard } from '../../types'
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Search,
  Sparkles,
  ShieldAlert,
  HelpCircle,
  ArrowRight,
} from 'lucide-react'
import Badge from '../ui/Badge'

export interface InsightCardComponentProps {
  insight: InsightCard
}

export const InsightCardComponent: React.FC<InsightCardComponentProps> = ({ insight }) => {
  const getCategoryMeta = (category: InsightCard['category']) => {
    switch (category) {
      case 'positive_trend':
        return {
          label: 'Positive Trend',
          variant: 'success' as const,
          icon: <TrendingUp className="w-3.5 h-3.5 mr-1" />,
        }
      case 'negative_trend':
        return {
          label: 'Negative Trend',
          variant: 'error' as const,
          icon: <TrendingDown className="w-3.5 h-3.5 mr-1" />,
        }
      case 'risk':
        return {
          label: 'Risk Detected',
          variant: 'error' as const,
          icon: <ShieldAlert className="w-3.5 h-3.5 mr-1" />,
        }
      case 'opportunity':
        return {
          label: 'Opportunity',
          variant: 'info' as const,
          icon: <Sparkles className="w-3.5 h-3.5 mr-1" />,
        }
      case 'unusual_value':
        return {
          label: 'Anomaly',
          variant: 'warning' as const,
          icon: <AlertTriangle className="w-3.5 h-3.5 mr-1" />,
        }
      case 'data_quality':
        return {
          label: 'Data Quality',
          variant: 'warning' as const,
          icon: <HelpCircle className="w-3.5 h-3.5 mr-1" />,
        }
      case 'investigate':
        return {
          label: 'Needs Review',
          variant: 'warning' as const,
          icon: <Search className="w-3.5 h-3.5 mr-1" />,
        }
      case 'important_finding':
      default:
        return {
          label: 'Key Finding',
          variant: 'info' as const,
          icon: <Sparkles className="w-3.5 h-3.5 mr-1" />,
        }
    }
  }

  const getConfidenceDot = (conf: InsightCard['confidence']) => {
    switch (conf) {
      case 'high':
        return <span className="w-2 h-2 rounded-full bg-emerald-500" title="High confidence" />
      case 'medium':
        return <span className="w-2 h-2 rounded-full bg-amber-500" title="Medium confidence" />
      case 'low':
      default:
        return <span className="w-2 h-2 rounded-full bg-rose-500" title="Low confidence" />
    }
  }

  const meta = getCategoryMeta(insight.category)

  return (
    <div className="bg-white rounded-xl border border-gray-200/80 p-5 shadow-sm hover:border-blue-200 transition-colors flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <Badge variant={meta.variant} className="flex items-center">
            {meta.icon}
            {meta.label}
          </Badge>
          <div className="flex items-center gap-1.5 text-xs text-gray-400 capitalize">
            {getConfidenceDot(insight.confidence)}
            <span>{insight.confidence} confidence</span>
          </div>
        </div>

        <h4 className="text-base font-semibold text-gray-900 mb-2 leading-snug">
          {insight.title}
        </h4>

        {insight.metric_value && (
          <div className="inline-block px-2.5 py-1 mb-2.5 bg-blue-50 border border-blue-100 rounded-lg text-xs font-semibold text-blue-800">
            {insight.metric_value}
          </div>
        )}

        <p className="text-sm text-gray-600 leading-relaxed mb-3">
          {insight.explanation}
        </p>

        {insight.evidence && (
          <div className="text-xs bg-gray-50 border border-gray-100 p-2.5 rounded-lg text-gray-600 font-mono mb-3">
            <span className="font-sans font-semibold text-gray-700">Evidence: </span>
            {insight.evidence}
          </div>
        )}

        {insight.warning && (
          <div className="flex items-start gap-2 p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 mb-3">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <span>{insight.warning}</span>
          </div>
        )}
      </div>

      {insight.suggested_action && (
        <div className="mt-3 pt-3 border-t border-gray-100 flex items-start gap-2 text-xs text-blue-700 italic bg-blue-50/40 p-2.5 rounded-lg">
          <ArrowRight className="w-3.5 h-3.5 text-blue-600 flex-shrink-0 mt-0.5 not-italic" />
          <span>
            <strong className="font-semibold not-italic text-blue-900">Suggested Action: </strong>
            {insight.suggested_action}
          </span>
        </div>
      )}
    </div>
  )
}

export default InsightCardComponent
