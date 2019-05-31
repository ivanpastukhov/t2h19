import numpy as np
import requests


class GeoParser:

    def __init__(self):
        pass

    @staticmethod
    def get_poly_points(poly_str):
        xy_str = poly_str.replace('POLYGON ((', '').replace('))', '')
        arr_xy_str = xy_str.split(',')
        arr_points_str = [tuple(s.split(' ')) for s in arr_xy_str]
        arr_points = [(float(x), float(y)) for (x, y) in arr_points_str]
        return arr_points

    @staticmethod
    def get_gravity_center(poly_str):
        P = GeoParser.get_poly_points(poly_str)
        len_ = len(P)

        #     print('P={}'.format(P))
        #     print('len_={}'.format(len_))

        A = 0
        for i in range(len_ - 1):
            pN = P[i]
            pN1 = P[i + 1]
            A += pN[0] * pN1[1] - pN1[0] * pN[1]
        A /= 2

        gr_x = 0
        for i in range(len_ - 1):
            pN = P[i]
            pN1 = P[i + 1]
            gr_x += (pN[0] + pN1[0]) * (pN[0] * pN1[1] - pN1[0] * pN[1])
        gr_x /= A * 6

        gr_y = 0
        for i in range(len_ - 1):
            pN = P[i]
            pN1 = P[i + 1]
            gr_y += (pN[1] + pN1[1]) * (pN[0] * pN1[1] - pN1[0] * pN[1])
        gr_y /= A * 6

        #     print('A={}'.format(A))
        #     print('gr_x={}'.format(gr_x))
        #     print('gr_y={}'.format(gr_y))
        lat = gr_x
        lon = gr_y
        return lon, lat

    @staticmethod
    def get_bounding_box(poly_str, add_offset=False):
        if add_offset:
            raise NotImplementedError('Frame is not implemented yet.')
        pts = GeoParser.get_poly_points(poly_str)
        xs, ys = list(zip(*pts))
        lat_min, lat_max, lon_min, lon_max = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
        return lat_min, lat_max, lon_min, lon_max

    @staticmethod
    def request_map(coord, im_size, zoom, gapi_key):
        """

        :param coord: These locations may be either specified as latitude/longitude values or as addresses.
        :param im_size: The size of the image.
        :param zoom: The following list shows the approximate level of detail you can expect to see at each zoom level:
                        1: World
                        5: Landmass/continent
                        10: City
                        15: Streets
                        20: Buildings
        :param gapi: Google Mapls API key
        :return: Content of the request object
        """
        url = f"https://maps.googleapis.com/maps/api/staticmap?center={coord}&zoom={zoom}&size={im_size}&maptype=satellite&key={gapi_key}"
        request = requests.get(url)
        if request.status_code != 200:
            request.raise_for_status()
        else:
            return request.content

    @staticmethod
    def poly2jpeg(poly_str, im_size, zoom, gapi_key, fname):
        """
        :param poly_str: string in Tele2Hack2.0 format
        :param im_size: size of image to be saved
        :param zoom: The following list shows the approximate level of detail you can expect to see at each zoom level:
                        1: World
                        5: Landmass/continent
                        10: City
                        15: Streets
                        20: Buildings
        :param gapi_key: Google Mapls API key
        :param fname: name of image file
        :return: -
        Save image
        """
        lon, lat = GeoParser.get_gravity_center(poly_str)
        coord = ", ".join(str(i) for i in [lon,lat])
        content = GeoParser.request_map(coord, im_size, zoom, gapi_key)
        with open(fname, 'wb') as fout:
            fout.write(content)
        return
