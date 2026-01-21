import { getDashboardData } from '@/lib/data';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FinanceDonut } from '@/components/dashboard/FinanceDonut';
import { MoodArea } from '@/components/dashboard/MoodArea';

// Disable caching to ensure real-time data
export const revalidate = 0;

export default async function Home() {
  const { transactions, journalEntries, activities, totalSpent, donutChartData, moodChartData } = await getDashboardData();

  const currencyFormatter = (number: number) => 
    `$${Intl.NumberFormat('es-AR').format(number).toString()}`;

  return (
    <main className="p-4 md:p-10 mx-auto max-w-7xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Life OS Dashboard</h1>
        <p className="text-muted-foreground">Resumen de actividad y métricas personales.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* 1. Finanzas - Resumen */}
        <Card className="max-w-lg mx-auto w-full">
          <CardHeader>
            <CardTitle>Gasto Total (Mes Actual)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
                {currencyFormatter(totalSpent)}
            </div>
            <div className="mt-4">
              {donutChartData.length > 0 ? (
                <FinanceDonut data={donutChartData} />
              ) : (
                <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
                  <p>Aún no hay gastos este mes</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 2. Journal - Mood Tracker */}
        <Card className="max-w-lg mx-auto md:col-span-2 w-full">
          <CardHeader>
            <CardTitle>Evolución de Ánimo (7 días)</CardTitle>
          </CardHeader>
          <CardContent>
            {moodChartData.length > 0 ? (
                <MoodArea data={moodChartData} />
            ) : (
                <div className="flex flex-col items-center justify-center h-72 text-muted-foreground">
                <p>No hay entradas de diario recientes</p>
                </div>
            )}
          </CardContent>
        </Card>

        {/* 3. Gym - Activity Log */}
        <Card className="max-w-lg mx-auto w-full">
          <CardHeader>
             <CardTitle>Gym & Salud</CardTitle>
          </CardHeader>
          <CardContent>
            {activities.length > 0 ? (
               <div className="space-y-4">
                {activities.map((activity) => (
                  <div key={activity.id} className="flex items-center space-x-4 border-b pb-4 last:border-0 last:pb-0">
                    <span className="text-2xl">🏃</span>
                    <div className="flex flex-col">
                      <span className="font-medium capitalize">
                        {activity.type || 'Actividad'}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {JSON.stringify(activity.details).slice(0, 30)}...
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-40 text-muted-foreground">
                 <p>Sin actividades recientes</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 4. Últimas Transacciones */}
        <Card className="max-w-lg mx-auto md:col-span-2 w-full">
          <CardHeader>
            <CardTitle>Últimas Transacciones</CardTitle>
          </CardHeader>
          <CardContent>
            {transactions.length > 0 ? (
              <div className="space-y-4">
                {transactions.slice(0, 5).map((t) => (
                  <div key={t.id} className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0">
                    <div className="flex items-center space-x-4">
                      <div className="flex flex-col">
                        <span className="font-medium">{t.merchant || 'Desconocido'}</span>
                        <span className="text-xs text-muted-foreground">{t.category || 'General'}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary">
                        {t.date_transaction}
                      </Badge>
                      <span className="font-semibold">{currencyFormatter(t.amount)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
               <div className="p-4 text-center text-muted-foreground">
                  <p>No hay transacciones recientes</p>
               </div>
            )}
          </CardContent>
        </Card>

      </div>
    </main>
  );
}
