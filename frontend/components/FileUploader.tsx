import { Button, UploadIcon } from './SvgIcons';

interface FileUploaderProps {
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleUpload: () => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ handleFileChange, handleUpload }) => {
  return (
    <div className="flex items-center mb-6">
      <input
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
        className="p-2 border border-gray-300 rounded-lg"
      />
      <Button onClick={handleUpload} className="ml-2">
        Upload PDF
        <UploadIcon className="w-5 h-5 ml-2" />
      </Button>
    </div>
  );
};

export default FileUploader;
