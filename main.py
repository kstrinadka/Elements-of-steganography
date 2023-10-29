from PIL import Image
import random

# Символы, которые будут обозначать конец сообщения.
end_of_secret_message = '++++++++++'


# Возвращаем список битов исходного текста.
def string_to_binary_chain(message_string):
    chain = list()
    for character in message_string:
        binary_string = '{0:08b}'.format(ord(character))  # Преобразуем символ в его двоичное представление (8 бит)
        for value in binary_string:
            chain.append(int(value))  # Преобразуем бит из строки в целое число и добавляем его в список
    return chain


# Преобразуем список бит в исходное сообщение.
def binary_chain_to_string(chain):
    message_string = ''
    chain_pointer = 0
    while chain_pointer + 8 <= len(chain):
        # Собираем 8 битов в одну строку
        binary_string = ''.join(str(x) for x in chain[chain_pointer:chain_pointer + 8])
        message_string += chr(int(binary_string, 2))  # Преобразуем 8 бит в символ
        chain_pointer += 8

        # Условия конца извлекаемого сообщения
        if len(message_string) > len(end_of_secret_message) \
                and message_string[-(len(end_of_secret_message)):] == end_of_secret_message:
            break
    return message_string[:-(len(end_of_secret_message))]


# Внедряем в конец каждого канала пикселя кучек информации исходного сообщения.
def encode_pixel(rgba_tuple, message_slice):
    # Вместо последнего бита в каждый из каналов вставляем бит из нашего исходного сообщения.
    binary_red = '{0:08b}'.format(rgba_tuple[0])[:7] + str(message_slice[0])
    binary_green = '{0:08b}'.format(rgba_tuple[1])[:7] + str(message_slice[1])
    binary_blue = '{0:08b}'.format(rgba_tuple[2])[:7] + str(message_slice[2])
    binary_alpha = '{0:08b}'.format(rgba_tuple[3])[:7] + str(message_slice[3])
    return (
        int(binary_red, base=2),
        int(binary_green, base=2),
        int(binary_blue, base=2),
        int(binary_alpha, base=2)
    )


# Извлекаем из каждого пикселя, зашитую в нем информацию.
def decode_pixel(rgba_tuple):
    binary_red = int('{0:08b}'.format(rgba_tuple[0])[-1], base=2)
    binary_green = int('{0:08b}'.format(rgba_tuple[1])[-1], base=2)
    binary_blue = int('{0:08b}'.format(rgba_tuple[2])[-1], base=2)
    binary_alpha = int('{0:08b}'.format(rgba_tuple[3])[-1], base=2)
    return [binary_red, binary_green, binary_blue, binary_alpha]


def encode_image(image_path, input_message, save_path):
    image = Image.open(image_path)
    image = image.convert("RGBA")

    # Список пикселей изображения. В одном пикселе содержится информация о 4 цветовых каналах.
    # Пиксель - кортеж из 4-х чисел (4 канала RGBA).
    pixel_list = image.getdata()
    input_message += end_of_secret_message
    bits_message_chain = string_to_binary_chain(input_message)
    message_pointer = 0
    encoded_pixel_list = list()
    for one_pixel in pixel_list:
        if message_pointer < len(bits_message_chain):
            encoded_pixel_list.append(encode_pixel(one_pixel, bits_message_chain[message_pointer:message_pointer + 4]))
            message_pointer += 4
        else:
            noise_chain = [0, 0, 0, 0]
            for i in range(4):
                noise_chain[i] = random.randint(0, 1)
            encoded_pixel_list.append(encode_pixel(one_pixel, noise_chain))
    image.putdata(encoded_pixel_list)
    image.save(save_path, "PNG")


def decode_image(image_path):
    im = Image.open(image_path)
    im = im.convert("RGBA")
    pixel_list = im.getdata()
    message_chain = list()
    for one_pixel in pixel_list:
        message_chain_list = decode_pixel(one_pixel)
        message_chain.append(message_chain_list[0])
        message_chain.append(message_chain_list[1])
        message_chain.append(message_chain_list[2])
        message_chain.append(message_chain_list[3])
    return binary_chain_to_string(message_chain)


input_message = input("Input stirng that will be injected into message \n")

encode_image('klichko.png', input_message, 'klichko2.png')
print('Message was injected to klichko2.png image')

print('Decoded message:')
print(decode_image('klichko2.png'))