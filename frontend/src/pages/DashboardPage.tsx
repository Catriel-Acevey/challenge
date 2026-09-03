import { NotificationForm } from '../components/NotificationForm';
import { NotificationList } from '../components/NotificationList';

export function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard de Notificaciones</h2>
        <p className="mt-1 text-sm text-gray-600">
          Gestiona tus notificaciones multicanal de forma sencilla.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulario de creación */}
        <div className="lg:col-span-1">
          <NotificationForm />
        </div>

        {/* Listado de notificaciones */}
        <div className="lg:col-span-2">
          <NotificationList />
        </div>
      </div>
    </div>
  );
}
