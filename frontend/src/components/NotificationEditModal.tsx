import { useState, useEffect } from 'react';
import { useUpdateNotification } from '../hooks/useNotifications';
import type { Notification, ChannelType } from '../types/api';

interface Props {
  notification: Notification;
  isOpen: boolean;
  onClose: () => void;
}

export function NotificationEditModal({ notification, isOpen, onClose }: Props) {
  const updateNotification = useUpdateNotification();
  const [title, setTitle] = useState(notification.title);
  const [content, setContent] = useState(notification.content);
  const [recipient, setRecipient] = useState(notification.recipient);
  const [channel, setChannel] = useState<ChannelType>(notification.channel);

  useEffect(() => {
    setTitle(notification.title);
    setContent(notification.content);
    setRecipient(notification.recipient);
    setChannel(notification.channel);
  }, [notification]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    updateNotification.mutate(
      { id: notification.id, data: { title, content } },
      { onSuccess: onClose }
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">✏️ Editar Notificación</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Título</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Contenido</label>
            <textarea
              required
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Canal</label>
            <select
              disabled
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-lg cursor-not-allowed"
            >
              <option value={channel}>{channel === 'email' ? '📧 Email' : channel === 'sms' ? '📱 SMS' : '🔔 Push'}</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Destinatario</label>
            <input
              type="text"
              disabled
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-lg cursor-not-allowed"
              value={recipient}
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition cursor-pointer">
              Cancelar
            </button>
            <button
              type="submit"
              disabled={updateNotification.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition cursor-pointer"
            >
              {updateNotification.isPending ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
