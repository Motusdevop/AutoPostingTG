import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Plus, Edit, Trash2, X, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from '@/components/ui/table'
import { ChannelStatus } from '@/components/ChannelStatus'
import { channelsApi } from '@/api/channels'
import { Channel } from '@/types/channel'
import { useToast } from '@/hooks/use-toast'

export default function Channels() {
	const navigate = useNavigate()
	const { toast } = useToast()
	const [search, setSearch] = useState('')
	const [itemsPerPage, setItemsPerPage] = useState(25)
	const [currentPage, setCurrentPage] = useState(1) // Текущая страница
	const [channels, setChannels] = useState<Channel[]>([])
	const [selectedChannels, setSelectedChannels] = useState<Set<number>>(
		new Set()
	)
	const [isModalOpen, setIsModalOpen] = useState(false)
	const [channelsToDelete, setChannelsToDelete] = useState<Set<number>>(
		new Set()
	)

	// Функция для получения каналов
	const fetchChannels = async () => {
		try {
			const data = await channelsApi.getAll()
			setChannels(data)
		} catch (error) {
			toast({
				title: 'Ошибка',
				description: 'Не удалось загрузить каналы',
				variant: 'destructive',
			})
		}
	}

	// Загрузка каналов один раз при монтировании компонента
	useEffect(() => {
		fetchChannels()
	}, [])

	// Настроим polling для обновления данных каждые 30 секунд
	useEffect(() => {
		const intervalId = setInterval(() => {
			fetchChannels()
		}, 30000)

		return () => clearInterval(intervalId)
	}, [])

	// Фильтрация каналов по поисковому запросу
	const filteredChannels = channels.filter(
		(channel: Channel) =>
			channel.name.toLowerCase().includes(search.toLowerCase()) ||
			channel.chat_id.toString().includes(search) ||
			channel.id.toString().includes(search)
	)

	// Логика для получения каналов на текущей странице
	const startIndex = (currentPage - 1) * itemsPerPage
	const paginatedChannels = filteredChannels.slice(
		startIndex,
		startIndex + itemsPerPage
	)

	// Обработчик выбора канала
	const handleChannelSelect = (id: number) => {
		setSelectedChannels(prevSelected => {
			const newSelected = new Set(prevSelected)
			if (newSelected.has(id)) {
				newSelected.delete(id)
			} else {
				newSelected.add(id)
			}
			return newSelected
		})
	}

	// Обработчик включения/выключения канала
	const handleToggleActive = async () => {
		if (selectedChannels.size === 0) return

		try {
			for (const id of selectedChannels) {
				const currentChannel = channels.find(channel => channel.id === id)
				if (currentChannel) {
					await channelsApi.toggleActive(id, !currentChannel.active)
				}
			}

			toast({
				title: 'Успех',
				description: `Статус каналов успешно обновлен`,
			})
			fetchChannels()
		} catch (error) {
			toast({
				title: 'Ошибка',
				description: 'Не удалось изменить статус каналов',
				variant: 'destructive',
			})
		}
	}

	// Открытие модального окна перед удалением
	const handleDeleteClick = () => {
		if (selectedChannels.size > 0) {
			setChannelsToDelete(new Set(selectedChannels)) // Устанавливаем каналы для удаления
			setIsModalOpen(true) // Открываем модальное окно
		} else {
			toast({
				title: 'Ошибка',
				description: 'Выберите каналы для удаления',
				variant: 'destructive',
			})
		}
	}

	// Подтверждение удаления
	const handleDelete = async () => {
		if (channelsToDelete.size === 0) return

		try {
			// Удаляем каждый выбранный канал
			for (const id of channelsToDelete) {
				await channelsApi.delete(id)
			}
			toast({
				title: 'Успех',
				description: 'Каналы успешно удалены',
			})
			fetchChannels() // Перезагружаем список каналов
		} catch (error) {
			toast({
				title: 'Ошибка',
				description: 'Не удалось удалить каналы',
				variant: 'destructive',
			})
		}

		// Закрываем модальное окно и сбрасываем состояния
		setIsModalOpen(false)
		setChannelsToDelete(new Set())
	}

	// Обработчик для перехода на страницу редактирования выбранного канала
	const handleEditClick = () => {
		if (selectedChannels.size === 1) {
			const selectedChannelId = Array.from(selectedChannels)[0]
			navigate(`/channels/${selectedChannelId}/edit`) // Переход на страницу редактирования канала
		} else {
			toast({
				title: 'Ошибка',
				description: 'Выберите только один канал для редактирования',
				variant: 'destructive',
			})
		}
	}

	// Переключение на следующую/предыдущую страницу
	const handlePageChange = (page: number) => {
		setCurrentPage(page)
	}

	const handleLogout = () => {
		localStorage.removeItem('auth_token') // Удаляем токен
		navigate('/login') // Перенаправляем на страницу входа
	}

	// Расчет количества страниц
	const totalPages = Math.ceil(filteredChannels.length / itemsPerPage)

	return (
		<div className='container mx-auto py-8'>
			<h1 className='text-2xl font-bold mb-8'>Управление телеграмм-каналами</h1>

			<div className='flex justify-between items-center mb-6'>
				<div className='flex gap-2 items-center'>
					<div className='relative'>
						<Input
							placeholder='Поиск...'
							value={search}
							onChange={e => setSearch(e.target.value)}
							className='pl-10 pr-10'
						/>
						<Search className='absolute left-3 top-2.5 h-5 w-5 text-gray-400' />
						{search && (
							<button
								onClick={() => setSearch('')}
								className='absolute right-3 top-2.5'
							>
								<X className='h-5 w-5 text-gray-400' />
							</button>
						)}
					</div>
					<Button variant='outline' onClick={handleLogout}>
						<LogOut className='mr-2 h-4 w-4' />
						Выйти
					</Button>
				</div>

				<div className='flex gap-2'>
					<Button onClick={() => navigate('/channels/new')}>
						<Plus className='mr-2 h-4 w-4' />
						Создать
					</Button>
					<Button
						variant='outline'
						onClick={handleEditClick}
						disabled={selectedChannels.size !== 1}
					>
						<Edit className='mr-2 h-4 w-4' />
						Изменить
					</Button>
					<Button variant='destructive' onClick={handleDeleteClick}>
						<Trash2 className='mr-2 h-4 w-4' />
						Удалить
					</Button>
					<Button
						variant='default'
						onClick={handleToggleActive}
						disabled={selectedChannels.size === 0}
					>
						{selectedChannels.size > 0
							? 'Включить/Выключить'
							: 'Нет выбранных каналов'}
					</Button>
				</div>
			</div>

			<div className='rounded-md border'>
				<Table>
					<TableHeader>
						<TableRow>
							<TableHead>Выбрать</TableHead>
							<TableHead>ID</TableHead>
							<TableHead>Статус</TableHead>
							<TableHead>Название</TableHead>
							<TableHead>Chat_ID</TableHead>
							<TableHead>Тип контента</TableHead>
							<TableHead>Интервал (мин)</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{paginatedChannels.map((channel: Channel) => (
							<TableRow
								key={channel.id}
								className={`cursor-pointer hover:bg-gray-50 ${
									selectedChannels.has(channel.id) ? 'bg-gray-100' : ''
								}`}
								onClick={() => handleChannelSelect(channel.id)}
							>
								<TableCell>
									<input
										type='checkbox'
										checked={selectedChannels.has(channel.id)}
										onChange={() => handleChannelSelect(channel.id)}
									/>
								</TableCell>
								<TableCell>{channel.id}</TableCell>
								<TableCell>
									<ChannelStatus active={channel.active} />
								</TableCell>
								<TableCell>{channel.name}</TableCell>
								<TableCell>{channel.chat_id}</TableCell>
								<TableCell>{channel.parse_mode}</TableCell>
								<TableCell>{channel.interval}</TableCell>
							</TableRow>
						))}
					</TableBody>
				</Table>
			</div>

			<div className='mt-4 flex justify-between items-center'>
				{/* Кнопки пагинации */}
				<div className='flex gap-2'>
					<Button
						onClick={() => handlePageChange(currentPage - 1)}
						disabled={currentPage === 1}
						className='text-black bg-white hover:bg-gray-100'
					>
						Назад
					</Button>
					<Button
						onClick={() => handlePageChange(currentPage + 1)}
						disabled={currentPage === totalPages}
						className='text-black bg-white hover:bg-gray-100'
					>
						Вперед
					</Button>
					<span className='text-black py-2'>{`Страница: ${currentPage}/${totalPages}`}</span>
				</div>

				{/* Количество элементов на странице */}
				<div>
					{[25, 50, 100].map(value => (
						<Button
							key={value}
							variant={itemsPerPage === value ? 'default' : 'outline'}
							onClick={() => setItemsPerPage(value)}
							className='text-black bg-white hover:bg-gray-100'
						>
							{value}
						</Button>
					))}
				</div>
			</div>

			{/* Модальное окно для подтверждения удаления */}
			{isModalOpen && (
				<div className='fixed inset-0 flex items-center justify-center bg-black bg-opacity-50'>
					<div className='bg-white p-6 rounded-md'>
						<h3 className='text-xl mb-4'>
							Вы уверены, что хотите удалить эти каналы?
						</h3>
						<div className='flex justify-end gap-4'>
							<Button variant='outline' onClick={() => setIsModalOpen(false)}>
								Отмена
							</Button>
							<Button variant='destructive' onClick={handleDelete}>
								Удалить
							</Button>
						</div>
					</div>
				</div>
			)}
		</div>
	)
}
