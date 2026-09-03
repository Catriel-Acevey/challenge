import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { notificationsApi } from '../services/api';
import type { NotificationCreateInput, NotificationUpdateInput } from '../types/api';

// ─── Query Keys ──────────────────────────────────────────────────────────────
export const notificationKeys = {
  all: ['notifications'] as const,
  lists: () => [...notificationKeys.all, 'list'] as const,
  detail: (id: number) => [...notificationKeys.all, 'detail', id] as const,
};

// ─── Hook: List Notifications ────────────────────────────────────────────────
export function useNotifications() {
  const {
    data: notifications = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: notificationKeys.lists(),
    queryFn: notificationsApi.getAll,
  });

  return { notifications, isLoading, error };
}

// ─── Hook: Create Notification ───────────────────────────────────────────────
export function useCreateNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: NotificationCreateInput) => notificationsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.all });
      toast.success('Notificación creada exitosamente');
    },
  });
}

// ─── Hook: Update Notification ───────────────────────────────────────────────
export function useUpdateNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: NotificationUpdateInput }) =>
      notificationsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.all });
      toast.success('Notificación actualizada');
    },
  });
}

// ─── Hook: Delete Notification ───────────────────────────────────────────────
export function useDeleteNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => notificationsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.all });
      toast.success('Notificación eliminada');
    },
  });
}
