import React from 'react'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  LineChart,
  Line
} from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { TrendingUp, PieChart as PieChartIcon, BarChart3, Activity } from 'lucide-react'

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4']

export const SkillCategoryChart = ({ analysis }) => {
  if (!analysis) return null

  // Prepare data for skill category comparison
  const categoryData = Object.keys(analysis.job_skills).map(category => {
    const jobSkills = analysis.job_skills[category] || []
    const matchingSkills = analysis.matching_skills[category] || []
    const missingSkills = analysis.missing_skills[category] || []
    
    return {
      category: category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      required: jobSkills.length,
      matched: matchingSkills.length,
      missing: missingSkills.length,
      matchRate: jobSkills.length > 0 ? (matchingSkills.length / jobSkills.length) * 100 : 0
    }
  }).filter(item => item.required > 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Skill Category Analysis
        </CardTitle>
        <CardDescription>
          Breakdown of skills by category showing matches vs requirements
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={categoryData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="category" 
              angle={-45}
              textAnchor="end"
              height={80}
              fontSize={12}
            />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [value, name === 'matched' ? 'Matched' : name === 'required' ? 'Required' : 'Missing']}
              labelFormatter={(label) => `Category: ${label}`}
            />
            <Bar dataKey="required" fill="#e5e7eb" name="required" />
            <Bar dataKey="matched" fill="#10b981" name="matched" />
            <Bar dataKey="missing" fill="#ef4444" name="missing" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export const ScoreBreakdownChart = ({ analysis }) => {
  if (!analysis) return null

  const scoreData = [
    { name: 'Content Similarity', value: analysis.similarity_score, color: '#3b82f6' },
    { name: 'Skill Match', value: analysis.skill_match_score, color: '#8b5cf6' },
    { name: 'Overall Match', value: analysis.composite_score, color: '#10b981' }
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <PieChartIcon className="h-5 w-5" />
          Score Breakdown
        </CardTitle>
        <CardDescription>
          Detailed breakdown of different scoring metrics
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={scoreData} layout="horizontal" margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis dataKey="name" type="category" width={120} />
            <Tooltip formatter={(value) => [`${value}%`, 'Score']} />
            <Bar dataKey="value" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export const KeywordOverlapChart = ({ analysis }) => {
  if (!analysis) return null

  const overlapData = [
    { 
      name: 'Matching Keywords', 
      value: analysis.matching_keywords.length, 
      color: '#10b981' 
    },
    { 
      name: 'Missing Keywords', 
      value: analysis.missing_keywords.length, 
      color: '#ef4444' 
    }
  ]

  const RADIAN = Math.PI / 180
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={14}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <PieChartIcon className="h-5 w-5" />
          Keyword Overlap Analysis
        </CardTitle>
        <CardDescription>
          Distribution of matching vs missing keywords
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={overlapData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomizedLabel}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {overlapData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value, name) => [value, name]} />
          </PieChart>
        </ResponsiveContainer>
        <div className="flex justify-center gap-6 mt-4">
          {overlapData.map((entry, index) => (
            <div key={index} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: entry.color }}
              ></div>
              <span className="text-sm text-gray-600">
                {entry.name}: {entry.value}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export const SkillRadarChart = ({ analysis }) => {
  if (!analysis) return null

  // Prepare radar chart data
  const radarData = Object.keys(analysis.job_skills).map(category => {
    const jobSkills = analysis.job_skills[category] || []
    const matchingSkills = analysis.matching_skills[category] || []
    
    return {
      category: category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      score: jobSkills.length > 0 ? (matchingSkills.length / jobSkills.length) * 100 : 0,
      fullMark: 100
    }
  }).filter(item => item.score > 0 || Object.keys(analysis.job_skills).includes(
    item.category.toLowerCase().replace(' ', '_')
  )).slice(0, 6) // Limit to 6 categories for better visualization

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Skill Proficiency Radar
        </CardTitle>
        <CardDescription>
          Your skill coverage across different categories
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={radarData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
            <PolarGrid />
            <PolarAngleAxis dataKey="category" fontSize={12} />
            <PolarRadiusAxis 
              angle={90} 
              domain={[0, 100]} 
              fontSize={10}
              tickFormatter={(value) => `${value}%`}
            />
            <Radar
              name="Skill Coverage"
              dataKey="score"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
              strokeWidth={2}
            />
            <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Coverage']} />
          </RadarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export const RecommendationPriorityChart = ({ analysis }) => {
  if (!analysis || !analysis.recommendations) return null

  // Create priority data based on recommendation types
  const priorityData = [
    { 
      priority: 'High Priority', 
      count: analysis.recommendations.filter(rec => 
        rec.includes('Consider adding') || rec.includes('Focus on')
      ).length,
      color: '#ef4444'
    },
    { 
      priority: 'Medium Priority', 
      count: analysis.recommendations.filter(rec => 
        rec.includes('Include') || rec.includes('Highlight')
      ).length,
      color: '#f59e0b'
    },
    { 
      priority: 'Low Priority', 
      count: analysis.recommendations.filter(rec => 
        rec.includes('Good') || rec.includes('Excellent')
      ).length,
      color: '#10b981'
    }
  ].filter(item => item.count > 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Recommendation Priority
        </CardTitle>
        <CardDescription>
          Breakdown of recommendations by priority level
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={priorityData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="priority" />
            <YAxis />
            <Tooltip formatter={(value) => [value, 'Recommendations']} />
            <Bar dataKey="count" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

