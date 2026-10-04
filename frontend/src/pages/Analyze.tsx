import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeConversation } from '../services/api';
import { Commitment } from '../types/commitment';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Textarea } from '../components/ui/Textarea';
import { Badge } from '../components/ui/Badge';
import { 
  Sparkles, 
  UploadCloud, 
  ArrowRight, 
  FileText, 
  Check, 
  Trash2,
  Clock
} from 'lucide-react';

const SAMPLE_CONVERSATION = `Rahul: Hey team, reviewed the feedback from ACME Corp. I'll send the updated SOW and the revised quotation tonight before 8 PM.
Priya: Sounds good. I'll make sure to share the revised presentation deck with their legal counsel by Friday noon.
Rahul: Perfect. Also, I will update the pricing sheet with tier discounts by tomorrow morning so you have the fresh figures.`;

export const Analyze: React.FC = () => {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState(SAMPLE_CONVERSATION);
  const [analyzing, setAnalyzing] = useState(false);
  const [extractedCommitments, setExtractedCommitments] = useState<Commitment[] | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    setAnalyzing(true);
    try {
      const res = await analyzeConversation(inputText);
      setExtractedCommitments(res.commitments);
    } catch (err) {
      console.error('Error analyzing conversation:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFileName(file.name);
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        if (content) {
          setInputText(content);
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-6">
      {/* Page Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-secondary/10 text-secondary text-xs font-semibold mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Commitment Detection</span>
        </div>
        <h1 className="font-headline text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
          Find commitments
        </h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Paste a conversation and PromiseOS will identify what was promised.
        </p>
      </div>

      {/* Input Section */}
      <Card className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
            Source Communication
          </span>
          <div className="flex items-center gap-2">
            {uploadedFileName && (
              <span className="text-xs text-secondary font-medium flex items-center gap-1">
                <FileText className="w-3.5 h-3.5" />
                {uploadedFileName}
              </span>
            )}
            <button
              onClick={() => {
                setInputText('');
                setUploadedFileName(null);
                setExtractedCommitments(null);
              }}
              className="text-xs text-on-surface-variant hover:text-rose-500 transition-colors flex items-center gap-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear text</span>
            </button>
          </div>
        </div>

        <Textarea
          rows={6}
          placeholder="Paste a conversation, meeting notes, or email..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          className="font-mono text-xs leading-relaxed"
        />

        {/* File dropzone / upload helper */}
        <label className="flex items-center justify-center gap-2.5 p-3.5 rounded-xl border border-dashed border-outline-variant hover:border-secondary/60 hover:bg-surface-container/50 cursor-pointer transition-all text-xs text-on-surface-variant">
          <UploadCloud className="w-4 h-4 text-secondary" />
          <span>Upload conversation file (TXT, PDF, EML, VTT)</span>
          <input
            type="file"
            accept=".txt,.pdf,.eml,.vtt,.md"
            className="hidden"
            onChange={handleFileUpload}
          />
        </label>

        {/* Analyze Action Button */}
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => setInputText(SAMPLE_CONVERSATION)}
            className="text-xs text-secondary hover:underline font-medium"
          >
            Load sample conversation
          </button>

          <Button
            variant="primary"
            onClick={handleAnalyze}
            loading={analyzing}
            disabled={!inputText.trim()}
            icon={<Sparkles className="w-4 h-4" />}
          >
            {analyzing ? 'Analyzing conversation...' : 'Analyze commitments'}
          </Button>
        </div>
      </Card>

      {/* Extracted Results */}
      {extractedCommitments && (
        <div className="flex flex-col gap-4 animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="flex items-center justify-between">
            <h2 className="font-headline text-lg font-semibold text-on-surface">
              {extractedCommitments.length} commitments found
            </h2>
            <Badge variant="success" size="sm">
              <Check className="w-3 h-3" />
              <span>Extracted successfully</span>
            </Badge>
          </div>

          <div className="flex flex-col gap-3">
            {extractedCommitments.map((c) => (
              <div
                key={c.id}
                onClick={() => navigate(`/commitments/${c.id}`)}
                className="group flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-surface-container-lowest border border-outline-variant/60 rounded-2xl shadow-subtle hover:shadow-card hover:border-outline-variant transition-all cursor-pointer gap-3"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-surface-container flex items-center justify-center text-xs font-semibold text-on-surface">
                    {c.person[0]}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-on-surface group-hover:text-secondary transition-colors">
                        {c.person}
                      </span>
                      <span className="text-xs text-on-surface-variant font-mono">
                        {c.id}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface font-medium mt-0.5">
                      {c.action}
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-3 shrink-0 pt-2 sm:pt-0 border-t border-outline-variant/40 sm:border-0">
                  <span className="inline-flex items-center gap-1 text-xs text-on-surface-variant font-medium">
                    <Clock className="w-3.5 h-3.5 text-secondary" />
                    {c.deadline}
                  </span>
                  <Button variant="secondary" size="sm">
                    <span>Review details</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <Button
              variant="outline"
              onClick={() => navigate('/commitments')}
            >
              View all commitments
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
