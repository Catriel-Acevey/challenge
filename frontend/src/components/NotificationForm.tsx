import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCreateNotification } from '../hooks/useNotifications';
import type { ChannelType } from '../types/api';

// ─── Zod Schema with Channel-Specific Validations ────────────────────────────
const notificationSchema = z
  .object({
    title: z.string().min(1, 'El título es requerido').max(255, 'Máximo 255 caracteres'),
    content: z.string().min(1, 'El contenido es requerido'),
    channel: z.enum(['email', 'sms', 'push']),
    recipient: z.string().min(1, 'El destinatario es requerido'),
  })
  .superRefine((data, ctx) => {
    if (data.channel === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(data.recipient)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'Debe ser un correo electrónico válido',
          path: ['recipient'],
        });
      }
    } else if (data.channel === 'sms') {
      const totalLength = data.title.length + data.content.length;
      if (totalLength > 160) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: `SMS excede los 160 caracteres (Actual: ${totalLength}/160)`,
          path: ['content'],
        });
      }
    } else if (data.channel === 'push') {
      if (data.recipient.length < 10) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'El token Push debe tener al menos 10 caracteres',
          path: ['recipient'],
        });
      }
    }
  });

type FormData = z.infer<typeof notificationSchema>;

// ─── Channel Config ──────────────────────────────────────────────────────────
const channelConfig: Record<ChannelType, { label: string; icon: string; placeholder: string }> = {
  email: { label: 'Correo Destinatario', icon: '📧', placeholder: 'destinatario@email.com' },
  sms: { label: 'Número de Teléfono', icon: '📱', placeholder: '+54 11 1234-5678' },
  push: { label: 'Token de Dispositivo', icon: '🔔', placeholder: 'Token del dispositivo (min 10 chars)' },
};

export function NotificationForm() {
  const createNotification = useCreateNotification();
  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(notificationSchema),
    defaultValues: { channel: 'email', title: '', content: '', recipient: '' },
  });

  const selectedChannel = watch('channel');
  const watchedTitle = watch('title') || '';
  const watchedContent = watch('content') || '';
  const smsCharCount = watchedTitle.length + watchedContent.length;

  const onSubmit = (data: FormData) => {
    createNotification.mutate(data, {
      onSuccess: () => reset(),
    });
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-100 dark:border-gray-700">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">📝 Nueva Notificación</h3>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Channel Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Canal</label>
          <div className="flex gap-2">
            {(['email', 'sms', 'push'] as const).map((ch) => (
              <label
                key={ch}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border-2 cursor-pointer transition text-sm font-medium ${
                  selectedChannel === ch
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 text-gray-600 dark:text-gray-400'
                }`}
              >
                <input type="radio" value={ch} {...register('channel')} className="sr-only" />
                <span>{channelConfig[ch].icon}</span>
                <span className="uppercase">{ch}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Título</label>
          <input
            {...register('title')}
            className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
            placeholder="Asunto de la notificación"
          />
          {errors.title && (
            <p className="text-red-500 text-xs mt-1">{errors.title.message}</p>
          )}
        </div>

        {/* Content */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Contenido</label>
          <textarea
            {...register('content')}
            rows={3}
            className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition resize-none"
            placeholder="Escribe el mensaje..."
          />
          {errors.content && (
            <p className="text-red-500 text-xs mt-1">{errors.content.message}</p>
          )}

          {/* SMS Character Counter */}
          {selectedChannel === 'sms' && (
            <div className="mt-1 flex items-center gap-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    smsCharCount > 160 ? 'bg-red-500' : smsCharCount > 140 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min((smsCharCount / 160) * 100, 100)}%` }}
                />
              </div>
              <span
                className={`text-xs font-mono font-bold ${
                  smsCharCount > 160 ? 'text-red-600' : smsCharCount > 140 ? 'text-yellow-600' : 'text-gray-500'
                }`}
              >
                {smsCharCount}/160
              </span>
            </div>
          )}
        </div>

        {/* Recipient */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {channelConfig[selectedChannel].label}
          </label>
          <input
            {...register('recipient')}
            className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
            placeholder={channelConfig[selectedChannel].placeholder}
          />
          {errors.recipient && (
            <p className="text-red-500 text-xs mt-1">{errors.recipient.message}</p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={createNotification.isPending}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-semibold focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition cursor-pointer"
        >
          {createNotification.isPending ? 'Creando...' : 'Crear Notificación'}
        </button>
      </form>
    </div>
  );
}
