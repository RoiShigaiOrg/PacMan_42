import mlx


class mlx_screen:

    def __init__(
            self,
            sess: mlx.Mlx,
            mlx_ptr,
            width: int,
            height: int,
            title: str) -> None:
        """
        Init method to create an mlx_window

        Parameters:
            mlx_ptr: ref to the mlx Session
            width: int that represent the pixel width of the screen
            height: int that represent the pixel height of the screen
            tittle: str displayed at the corresponding screen

        Return:
            return a mlx_screen Class
        """
        self.__session = sess
        self.__dimension = tuple(width, height)
        self.__title = title
        self.__win_ptr = sess.mlx_new_window(mlx_ptr, width, height, title)

    def clear(self, mlx_ptr) -> None:
        """
        clear the window completely
        """
        self.__session.mlx_clear_window(mlx_ptr, self.__win_ptr)

    def size(self) -> tuple:
        """
        Return a tuple containing the size in pixel of the window

        tuple: (x: int, y: int)
        """
        return tuple(self.__width, self.__height)

    def create_form(self, width: int, height: int):
        """
        Return a data buffer containing 'width' * 'heigth' pixel

        This buffer can be use to write image/form in it
        """
        result = mlx.mlx_new_image(self.__session, width, height)
        if result:
            return result
        return None

    def draw(self, img, x: int, y: int) -> None:
        mlx.mlx_put_image_to_window(self.__session, self.__win_ptr, img, x, y)
