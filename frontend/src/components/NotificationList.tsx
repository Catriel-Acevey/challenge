import { useState } from 'react';
import { useNotifications, useDeleteNotification } from '../hooks/useNotifications';
import type { ChannelType, NotificationStatus } from '../types/api';

// ─── Style Config ────────────────────────────────────────────────────────────
const statusStyles: Record<NotificationStatus, { bg: string; text: string; label: string }> = {
  pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: '⏳ Pendiente' },
  sent: { bg: 'bg-green-100', text: 'text-green-800', label: '✅ Enviado' },
  failed: { bg: 'bg-red-100', text: 'text-red-800', label: '❌ Fallido' },
};

const channelIcons: Record<ChannelType, string> = {
  email: '📧',
  sms: '📱',
  push: '🔔',
};

export function NotificationList() {
  const { notifications, isLoading } = useNotifications();
  const deleteNotification = useDeleteNotification();
  const [filterChannel, setFilterChannel] = useState<ChannelType | 'all'>('all');

  const filtered =
    filterChannel === 'all' ? notifications : notifications.filter((n) => n.channel === filterChannel);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <h3 className="text-lg font-bold text-gray-900">
            📋 Mis Notificaciones
            <span className="ml-2 text-sm font-normal text-gray-500">({filtered.length})</span>
          </h3>

          <select
            value={filterChannel}
            onChange={(e) => setFilterChannel(e.target.value as ChannelType | 'all')}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          >
            <option value="all">Todos los canales</option>
            <option value="email">📧 Email</option>
            <option value="sms">📱 SMS</option>
            <option value="push">🔔 Push</option>
          </select>
        </div>
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <div className="p-12 text-center text-gray-500">
          <span className="text-4xl block mb-3">📭</span>
          <p className="font-medium">No hay notificaciones{filterChannel !== 'all' ? ` en ${filterChannel}` : ''}</p>
          <p className="text-sm mt-1">Crea tu primera notificación usando el formulario.</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100">
          {filtered.map((item) => {
            const status = statusStyles[item.status];
            return (
              <div key={item.id} className="p-4 hover:bg-gray-50 transition">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{channelIcons[item.channel]}</span>
                      <h4 className="font-semibold text-gray-900 truncate">{item.title}</h4>
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${status.bg} ${status.text}`}
                      >
                        {status.label}
                      </span>
                    </div>

                    <p className="text-sm text-gray-600 line-clamp-2 mb-1">{item.content}</p>

                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>Para: <span className="text-gray-600">{item.recipient}</span></span>
                      <span>{new Date(item.created_at).toLocaleString('es-AR')}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      if (window.confirm('¿Estás seguro de eliminar esta notificación?')) {
                        deleteNotification.mutate(item.id);
                      }
                    }}
                    disabled={deleteNotification.isPending}
                    className="text-red-400 hover:text-red-600 p-2 rounded-lg hover:bg-red-50 transition disabled:opacity-50 cursor-pointer flex-shrink-0"
                    title="Eliminar"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
