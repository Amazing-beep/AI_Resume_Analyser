import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Upload, FileText, Brain, TrendingUp, CheckCircle, AlertCircle, Lightbulb, BarChart3, PieChart } from 'lucide-react'
import { 
  SkillCategoryChart, 
  ScoreBreakdownChart, 
  KeywordOverlapChart, 
  SkillRadarChart, 
  RecommendationPriorityChart 
} from './components/AnalysisCharts.jsx'
import './App.css'

function App() {
  const [resumeFile, setResumeFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (file) {
      setResumeFile(file)
      setError('')
    }
  }

  const handleAnalyze = async () => {
    if (!resumeFile || !jobDescription.trim()) {
      setError('Please upload a resume and enter a job description')
      return
    }

    setLoading(true)
    setError('')

    const formData = new FormData()
    formData.append('resume', resumeFile)
    formData.append('job_description', jobDescription)

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success) {
        setAnalysis(data.analysis)
      } else {
        setError(data.error || 'Analysis failed')
      }
    } catch (err) {
      setError('Failed to connect to the server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBackground = (score) => {
    if (score >= 70) return 'bg-green-100'
    if (score >= 50) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center justify-center gap-3">
            <Brain className="h-10 w-10 text-blue-600" />
            AI Resume Analyzer
          </h1>
          <p className="text-lg text-gray-600">
            Get intelligent insights on how well your resume matches job requirements
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="space-y-6">
            {/* Resume Upload */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Upload Resume
                </CardTitle>
                <CardDescription>
                  Upload your resume in PDF, DOCX, or TXT format
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
                    <Input
                      type="file"
                      accept=".pdf,.docx,.txt"
                      onChange={handleFileChange}
                      className="hidden"
                      id="resume-upload"
                    />
                    <Label htmlFor="resume-upload" className="cursor-pointer">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-sm text-gray-600">
                        {resumeFile ? resumeFile.name : 'Click to upload or drag and drop'}
                      </p>
                    </Label>
                  </div>
                  {resumeFile && (
                    <div className="flex items-center gap-2 text-sm text-green-600">
                      <CheckCircle className="h-4 w-4" />
                      File uploaded: {resumeFile.name}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Job Description */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Job Description
                </CardTitle>
                <CardDescription>
                  Paste the job description you want to match against
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Textarea
                  placeholder="Paste the job description here..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="min-h-[200px] resize-none"
                />
                <p className="text-sm text-gray-500 mt-2">
                  {jobDescription.length} characters
                </p>
              </CardContent>
            </Card>

            {/* Analyze Button */}
            <Button
              onClick={handleAnalyze}
              disabled={loading || !resumeFile || !jobDescription.trim()}
              className="w-full h-12 text-lg"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Analyze Resume
                </>
              )}
            </Button>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {analysis ? (
              <>
                {/* Score Overview */}
                <Card>
                  <CardHeader>
                    <CardTitle>Analysis Results</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Composite Score */}
                    <div className={`p-4 rounded-lg ${getScoreBackground(analysis.composite_score)}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold">Overall Match</span>
                        <span className={`text-2xl font-bold ${getScoreColor(analysis.composite_score)}`}>
                          {analysis.composite_score}%
                        </span>
                      </div>
                      <Progress value={analysis.composite_score} className="h-2" />
                    </div>

                    {/* Individual Scores */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {analysis.similarity_score}%
                        </div>
                        <div className="text-sm text-gray-600">Content Similarity</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {analysis.skill_match_score}%
                        </div>
                        <div className="text-sm text-gray-600">Skill Match</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Detailed Analysis with Tabs */}
                <Card>
                  <CardHeader>
                    <CardTitle>Detailed Analysis</CardTitle>
                    <CardDescription>
                      Comprehensive breakdown with interactive visualizations
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Tabs defaultValue="overview" className="w-full">
                      <TabsList className="grid w-full grid-cols-4">
                        <TabsTrigger value="overview">Overview</TabsTrigger>
                        <TabsTrigger value="skills">Skills</TabsTrigger>
                        <TabsTrigger value="charts">Charts</TabsTrigger>
                        <TabsTrigger value="recommendations">Tips</TabsTrigger>
                      </TabsList>
                      
                      <TabsContent value="overview" className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <ScoreBreakdownChart analysis={analysis} />
                          <KeywordOverlapChart analysis={analysis} />
                        </div>
                      </TabsContent>
                      
                      <TabsContent value="skills" className="space-y-4">
                        {/* Matching Skills */}
                        <div>
                          <h4 className="font-semibold text-green-700 mb-2 flex items-center gap-2">
                            <CheckCircle className="h-4 w-4" />
                            Matching Skills ({analysis.matching_keywords.length})
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {analysis.matching_keywords.slice(0, 15).map((skill, index) => (
                              <Badge key={index} variant="secondary" className="bg-green-100 text-green-800">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        {/* Missing Skills */}
                        {analysis.missing_keywords.length > 0 && (
                          <div>
                            <h4 className="font-semibold text-orange-700 mb-2 flex items-center gap-2">
                              <AlertCircle className="h-4 w-4" />
                              Missing Keywords ({analysis.missing_keywords.length})
                            </h4>
                            <div className="flex flex-wrap gap-2">
                              {analysis.missing_keywords.map((skill, index) => (
                                <Badge key={index} variant="outline" className="border-orange-300 text-orange-700">
                                  {skill}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </TabsContent>
                      
                      <TabsContent value="charts" className="space-y-4">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                          <SkillCategoryChart analysis={analysis} />
                          <SkillRadarChart analysis={analysis} />
                        </div>
                        <RecommendationPriorityChart analysis={analysis} />
                      </TabsContent>
                      
                      <TabsContent value="recommendations" className="space-y-4">
                        <div className="space-y-3">
                          {analysis.recommendations.map((rec, index) => (
                            <div key={index} className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                              <Lightbulb className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                              <div>
                                <p className="text-sm text-gray-700 font-medium">{rec}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </TabsContent>
                    </Tabs>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Brain className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">
                    Ready to Analyze
                  </h3>
                  <p className="text-gray-500">
                    Upload your resume and enter a job description to get started
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

