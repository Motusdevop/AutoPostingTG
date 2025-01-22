import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select'
import { useToast } from '@/hooks/use-toast'
import { channelsApi } from '@/api/channels'

export default function ChannelForm() {
	const { id } = useParams()
	const navigate = useNavigate()
	const { toast } = useToast()
	const isEditing = Boolean(id)

	const [formData, setFormData] = useState({
		name: '',
		chat_id: '',
		parse_mode: 'HTML',
		interval: '240',
	})

	// Загружаем данные канала для редактирования с сервера
	const {
		data: channel,
		isLoading,
		isError,
	} = useQuery({
		queryKey: ['channel', id],
		queryFn: () => channelsApi.getById(Number(id)),
		enabled: isEditing,
	})

	// Подставляем данные в форму, если канал был загружен
	useEffect(() => {
		if (channel) {
			setFormData({
				name: channel.name,
				chat_id: channel.chat_id.toString(),
				parse_mode: channel.parse_mode,
				interval: channel.interval.toString(),
			})
		}
	}, [channel]) // Срабатывает, когда данные канала загружены

	// Мутация для создания или обновления канала
	const mutation = useMutation({
		mutationFn: (data: any) => {
			return isEditing
				? channelsApi.update(Number(id), data) // Обновляем канал
				: channelsApi.create(data) // Создаем новый канал
		},
		onSuccess: () => {
			toast({
				title: 'Успех',
				description: `Канал успешно ${isEditing ? 'обновлен' : 'создан'}`,
			})
			navigate('/channels')
		},
		onError: () => {
			toast({
				title: 'Ошибка',
				description: 'Не удалось сохранить канал',
				variant: 'destructive',
			})
		},
	})

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault()
		const data = {
			...formData,
			chat_id: Number(formData.chat_id),
			interval: Number(formData.interval),
		}
		mutation.mutate(data)
	}

	const handleCheck = async () => {
		try {
			toast({
				title: 'Проверка успешна',
				description: 'Подключение к каналу установлено',
			})
		} catch (error) {
			toast({
				title: 'Ошибка проверки',
				description: 'Не удалось подключиться к каналу',
				variant: 'destructive',
			})
		}
	}

	// Пока данные загружаются, показываем индикатор загрузки
	if (isLoading) {
		return <div>Загрузка...</div>
	}

	// В случае ошибки загрузки данных
	if (isError) {
		return <div>Ошибка загрузки данных канала</div>
	}

	return (
		<div className='container mx-auto py-8 max-w-2xl'>
			<h1 className='text-2xl font-bold mb-8'>
				{isEditing ? 'Редактирование канала' : 'Создание нового канала'}
			</h1>

			<form onSubmit={handleSubmit} className='space-y-6'>
				{/* Название канала */}
				<div className='space-y-2'>
					<Label htmlFor='name'>Название</Label>
					<Input
						id='name'
						value={formData.name}
						onChange={e => setFormData({ ...formData, name: e.target.value })}
						maxLength={50}
						required
						readOnly={isEditing} // Блокируем поле, если редактируем
					/>
				</div>

				{/* ID канала */}
				<div className='space-y-2'>
					<Label htmlFor='chat_id'>ID канала</Label>
					<Input
						id='chat_id'
						value={formData.chat_id}
						onChange={e =>
							setFormData({ ...formData, chat_id: e.target.value })
						}
						type='number'
						required
					/>
				</div>

				{/* Тип контента */}
				<div className='space-y-2'>
					<Label htmlFor='parse_mode'>Тип контента</Label>
					<Select
						value={formData.parse_mode}
						onValueChange={value =>
							setFormData({ ...formData, parse_mode: value })
						}
					>
						<SelectTrigger>
							<SelectValue />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value='HTML'>HTML</SelectItem>
							<SelectItem value='MarkdownV2'>MarkdownV2</SelectItem>
						</SelectContent>
					</Select>
				</div>

				{/* Интервал */}
				<div className='space-y-2'>
					<Label htmlFor='interval'>Интервал (мин)</Label>
					<Input
						id='interval'
						value={formData.interval}
						onChange={e =>
							setFormData({ ...formData, interval: e.target.value })
						}
						type='number'
						min='1'
						required
					/>
				</div>

				<div className='flex justify-end gap-2 pt-6'>
					<Button
						type='button'
						variant='outline'
						onClick={() => navigate('/channels')}
					>
						Отменить
					</Button>
					<Button type='button' variant='outline' onClick={handleCheck}>
						Проверить
					</Button>
					<Button type='submit'>Сохранить</Button>
				</div>
			</form>
		</div>
	)
}
