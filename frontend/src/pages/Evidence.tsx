import React, { useState, useEffect } from 'react';
import { getEvidence, uploadEvidence } from '../services/api';
import { EvidenceItem } from '../types/evidence';
import { EvidenceCard } from '../components/evidence/EvidenceCard';
import { EvidencePreview } from '../components/evidence/EvidencePreview';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Search, UploadCloud, FolderCheck, Plus } from 'lucide-react';

export const Evidence: React.FC = () => {
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [previewItem, setPreviewItem] = useState<EvidenceItem | null>(null);

  // Upload modal state
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await getEvidence();
        setEvidenceList(data);
      } catch (err) {
        console.error('Failed to load evidence:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleUploadSubmit = async () => {
    if (!uploadFile) return;
    setUploading(true);
    try {
      const newItem = await uploadEvidence(uploadFile);
      setEvidenceList((prev) => [newItem, ...prev]);
      setUploadModalOpen(false);
      setUploadFile(null);
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setUploading(false);
    }
  };

  const filterTabs = [
    { id: 'all', label: 'All Evidence', count: evidenceList.length },
    { id: 'Supporting', label: 'Supporting', count: evidenceList.filter((e) => e.status === 'Supporting').length },
    { id: 'Partial Match', label: 'Partial Match', count: evidenceList.filter((e) => e.status === 'Partial Match').length },
    { id: 'Missing Items', label: 'Missing Items', count: evidenceList.filter((e) => e.status === 'Missing Items').length },
  ];

  const filteredEvidence = evidenceList.filter((item) => {
    const matchesSearch =
      item.fileName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.relatedCommitment.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;
    if (selectedFilter === 'all') return true;
    return item.status === selectedFilter;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-headline text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
            Evidence
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            Evidence used to verify your commitments.
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => setUploadModalOpen(true)}
          icon={<Plus className="w-4 h-4" />}
          className="self-start sm:self-auto"
        >
          Add Evidence
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <Card className="p-3 sm:p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {filterTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedFilter(tab.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all flex items-center gap-1.5 shrink-0 ${
                selectedFilter === tab.id
                  ? 'bg-primary text-on-primary'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
              }`}
            >
              <span>{tab.label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                selectedFilter === tab.id
                  ? 'bg-white/20 text-white'
                  : 'bg-surface-container text-on-surface-variant'
              }`}>
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="w-full md:w-72 shrink-0">
          <Input
            placeholder="Search evidence files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon={<Search className="w-4 h-4 text-on-surface-variant" />}
          />
        </div>
      </Card>

      {/* Evidence Cards */}
      <div className="flex flex-col gap-3">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-12 bg-surface-container-lowest rounded-2xl border border-outline-variant/60">
            <span className="w-6 h-6 border-2 border-secondary border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-xs text-on-surface-variant">Loading evidence files...</p>
          </div>
        ) : filteredEvidence.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 bg-surface-container-lowest rounded-2xl border border-outline-variant/60 text-center">
            <FolderCheck className="w-8 h-8 text-on-surface-variant/60 mb-2" />
            <h3 className="font-headline text-sm font-semibold text-on-surface">
              No evidence found
            </h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-sm">
              {searchQuery
                ? 'No evidence items match your search.'
                : 'No evidence files in this status.'}
            </p>
          </div>
        ) : (
          filteredEvidence.map((e) => (
            <EvidenceCard
              key={e.id}
              evidence={e}
              onView={(item) => setPreviewItem(item)}
            />
          ))
        )}
      </div>

      {/* Evidence Preview Modal */}
      <EvidencePreview
        evidence={previewItem}
        isOpen={Boolean(previewItem)}
        onClose={() => setPreviewItem(null)}
      />

      {/* Upload Evidence Modal */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Add Evidence"
        description="Upload deliverable files (PDF, XLSX, CSV, DOCX) to verify against active promises."
        maxWidth="md"
      >
        <div className="flex flex-col gap-4">
          <label className="flex flex-col items-center justify-center gap-3 p-6 rounded-2xl border-2 border-dashed border-outline-variant hover:border-secondary/60 hover:bg-surface-container/40 cursor-pointer transition-all text-center">
            <UploadCloud className="w-8 h-8 text-secondary" />
            <div>
              <p className="text-sm font-semibold text-on-surface">
                {uploadFile ? uploadFile.name : 'Click to select or drag and drop deliverable'}
              </p>
              <p className="text-xs text-on-surface-variant mt-0.5">
                {uploadFile ? `${(uploadFile.size / 1024).toFixed(1)} KB` : 'PDF, XLSX, DOCX, CSV up to 25MB'}
              </p>
            </div>
            <input
              type="file"
              accept=".pdf,.xlsx,.docx,.csv,.txt"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  setUploadFile(e.target.files[0]);
                }
              }}
            />
          </label>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-outline-variant/60">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setUploadModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              disabled={!uploadFile}
              loading={uploading}
              onClick={handleUploadSubmit}
            >
              Upload & Process
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
