export type ToastMessage = {
  id: number;
  kind: 'success' | 'error';
  text: string;
};

export function Toast({ message, onClose }: { message: ToastMessage; onClose: (id: number) => void }) {
  const color = message.kind === 'success' ? 'bg-emerald-700' : 'bg-red-700';
  return (
    <div className={`rounded px-3 py-2 text-sm text-white shadow ${color}`}>
      <div className="flex items-center gap-3">
        <span className="flex-1">{message.text}</span>
        <button className="text-xs opacity-80 hover:opacity-100" onClick={() => onClose(message.id)}>
          Close
        </button>
      </div>
    </div>
  );
}
