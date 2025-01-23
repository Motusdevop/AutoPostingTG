import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'

const API_URL = process.env.BACKEND_URL;

export default function Login() {
	const navigate = useNavigate()
	const { toast } = useToast()
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [loading, setLoading] = useState(false) // Для состояния загрузки

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setLoading(true) // Включаем индикатор загрузки

		const token = btoa(`${username}:${password}`)
		try {
			const response = await fetch(`${API_URL}channels/get_all`, {
				headers: {
					Authorization: `Basic ${token}`,
				},
			})

			if (response.ok) {
				// Если авторизация прошла успешно
				localStorage.setItem('auth_token', token) // Сохраняем токен в localStorage
				toast({
					title: 'Успех',
					description: 'Авторизация успешна',
				})
				navigate('/channels')
			} else {
				// Если ошибка авторизации (например, 401)
				toast({
					title: 'Ошибка',
					description: 'Неверные учетные данные',
					variant: 'destructive',
				})
			}
		} catch (error) {
			// Если ошибка подключения к серверу
			toast({
				title: 'Ошибка',
				description: 'Ошибка при подключении к серверу',
				variant: 'destructive',
			})
		} finally {
			setLoading(false) // Снимаем индикатор загрузки
		}
	}

	return (
		<div className='container mx-auto max-w-md py-16'>
			<h1 className='text-2xl font-bold mb-8'>Вход в систему</h1>

			<form onSubmit={handleSubmit} className='space-y-6'>
				<div className='space-y-2'>
					<Label htmlFor='username'>Имя пользователя</Label>
					<Input
						id='username'
						value={username}
						onChange={e => setUsername(e.target.value)}
						required
					/>
				</div>

				<div className='space-y-2'>
					<Label htmlFor='password'>Пароль</Label>
					<Input
						id='password'
						type='password'
						value={password}
						onChange={e => setPassword(e.target.value)}
						required
					/>
				</div>

				<Button
					type='submit'
					className='w-full'
					disabled={loading} // Блокируем кнопку при загрузке
				>
					{loading ? 'Загрузка...' : 'Войти'}
				</Button>
			</form>
		</div>
	)
}
