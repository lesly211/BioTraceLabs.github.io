"""
Módulo de comparación de imágenes de cortes transversales de madera.
Utiliza múltiples algoritmos de visión por computadora para determinar
si dos fotos corresponden a la misma troza de madera.
"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from pathlib import Path
import traceback


class ComparadorImagenes:
    """
    Compara dos imágenes de cortes transversales de madera usando múltiples métricas:
    - Detección automática del círculo del corte transversal
    - Eliminación del fondo para comparar solo la madera
    - SSIM (Structural Similarity Index): Compara la estructura y patrones
    - Histograma de color: Compara distribución de colores
    - ORB Feature Matching: Detecta y compara características únicas (anillos, patrones)
    - MSE (Mean Squared Error): Error promedio entre píxeles
    """
    
    def __init__(self):
        self.orb = cv2.ORB_create(nfeatures=500)
        self.bf_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    def detectar_y_recortar_circulo(self, img):
        """
        Detecta el círculo del corte transversal y aplica una máscara para eliminar el fondo.
        
        Args:
            img: Imagen BGR
            
        Returns:
            tuple: (imagen con máscara aplicada, máscara binaria, círculo detectado)
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplicar desenfoque para reducir ruido
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detectar círculos usando la transformada de Hough
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=gray.shape[0] // 4,
            param1=50,
            param2=30,
            minRadius=int(gray.shape[0] * 0.2),
            maxRadius=int(gray.shape[0] * 0.6)
        )
        
        # Crear máscara
        mask = np.zeros(gray.shape, dtype=np.uint8)
        circulo_info = None
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            # Tomar el círculo más grande (probablemente el corte)
            circle = circles[0][0]
            x, y, r = circle[0], circle[1], circle[2]
            circulo_info = (x, y, r)
            
            # Crear máscara circular
            cv2.circle(mask, (x, y), r, 255, -1)
        else:
            # Si no se detecta círculo, usar detección de bordes como fallback
            edges = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Encontrar el contorno más grande
                largest_contour = max(contours, key=cv2.contourArea)
                # Obtener el círculo envolvente mínimo
                (x, y), radius = cv2.minEnclosingCircle(largest_contour)
                x, y, r = int(x), int(y), int(radius)
                circulo_info = (x, y, r)
                cv2.circle(mask, (x, y), r, 255, -1)
            else:
                # Si todo falla, usar toda la imagen
                mask = np.ones(gray.shape, dtype=np.uint8) * 255
                circulo_info = (gray.shape[1]//2, gray.shape[0]//2, min(gray.shape)//2)
        
        # Aplicar máscara a la imagen original
        img_masked = cv2.bitwise_and(img, img, mask=mask)
        
        return img_masked, mask, circulo_info
    
    def comparar_imagenes(self, ruta_imagen1, ruta_imagen2):
        """
        Compara dos imágenes y retorna un diccionario con métricas de similitud.
        Detecta automáticamente el círculo del corte y elimina el fondo.
        
        Args:
            ruta_imagen1 (str): Ruta a la primera imagen (foto del titular)
            ruta_imagen2 (str): Ruta a la segunda imagen (foto del centro)
        
        Returns:
            dict: Diccionario con similitud_porcentaje, detalles de métricas y coincidencia
        """
        try:
            # Cargar imágenes
            img1 = cv2.imread(str(ruta_imagen1))
            img2 = cv2.imread(str(ruta_imagen2))
            
            if img1 is None or img2 is None:
                return {
                    "success": False,
                    "error": "No se pudieron cargar las imágenes para comparación"
                }
            
            # Redimensionar para que tengan el mismo tamaño (importante para SSIM)
            height, width = 512, 512
            img1_resized = cv2.resize(img1, (width, height))
            img2_resized = cv2.resize(img2, (width, height))
            
            # Detectar y recortar círculos (eliminar fondo)
            print("[Comparación] Detectando círculo del corte en imagen 1...")
            img1_masked, mask1, circle1 = self.detectar_y_recortar_circulo(img1_resized)
            print(f"[Comparación] Círculo detectado: centro=({circle1[0]}, {circle1[1]}), radio={circle1[2]}")
            
            print("[Comparación] Detectando círculo del corte en imagen 2...")
            img2_masked, mask2, circle2 = self.detectar_y_recortar_circulo(img2_resized)
            print(f"[Comparación] Círculo detectado: centro=({circle2[0]}, {circle2[1]}), radio={circle2[2]}")
            
            # Usar las imágenes con máscara para comparación
            img1_resized = img1_masked
            img2_resized = img2_masked
            
            # Combinar máscaras para usar solo la región común
            mask_combined = cv2.bitwise_and(mask1, mask2)
            
            # 1. SSIM - Structural Similarity (mejor para patrones de madera)
            similitud_ssim = self._calcular_ssim(img1_resized, img2_resized, mask_combined)
            
            # 2. Comparación de histogramas (distribución de colores)
            similitud_histograma = self._comparar_histogramas(img1_resized, img2_resized, mask_combined)
            
            # 3. Feature Matching con ORB (detecta patrones únicos de anillos)
            similitud_features, num_coincidencias = self._comparar_features(img1_resized, img2_resized, mask_combined)
            
            # 4. MSE - Mean Squared Error (menor es mejor)
            mse_value = self._calcular_mse(img1_resized, img2_resized, mask_combined)
            
            # Calcular similitud ponderada final
            # SSIM tiene más peso porque es mejor para estructuras de madera
            peso_ssim = 0.40
            peso_histograma = 0.25
            peso_features = 0.35
            
            similitud_total = (
                similitud_ssim * peso_ssim +
                similitud_histograma * peso_histograma +
                similitud_features * peso_features
            ) * 100
            
            # Determinar nivel de coincidencia
            if similitud_total >= 75:
                nivel = "ALTA"
                coincide = True
                mensaje = "Las imágenes muestran alta similitud. Es muy probable que sea la misma troza."
            elif similitud_total >= 60:
                nivel = "MEDIA"
                coincide = True
                mensaje = "Las imágenes muestran similitud moderada. Posiblemente sea la misma troza."
            elif similitud_total >= 45:
                nivel = "BAJA"
                coincide = False
                mensaje = "Las imágenes muestran baja similitud. Requiere verificación adicional."
            else:
                nivel = "MUY BAJA"
                coincide = False
                mensaje = "Las imágenes son significativamente diferentes. Probablemente NO sea la misma troza."
            
            return {
                "success": True,
                "similitud_porcentaje": round(similitud_total, 2),
                "coincide": coincide,
                "nivel_similitud": nivel,
                "mensaje": mensaje,
                "metricas_detalladas": {
                    "ssim": round(similitud_ssim * 100, 2),
                    "histograma": round(similitud_histograma * 100, 2),
                    "features": round(similitud_features * 100, 2),
                    "mse": round(mse_value, 2),
                    "num_coincidencias_features": num_coincidencias
                },
                "interpretacion": {
                    "ssim": self._interpretar_ssim(similitud_ssim),
                    "histograma": self._interpretar_histograma(similitud_histograma),
                    "features": self._interpretar_features(similitud_features, num_coincidencias)
                }
            }
            
        except Exception as e:
            print(f"[ComparadorImagenes] Error: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Error al comparar imágenes: {str(e)}"
            }
    
    def _calcular_ssim(self, img1, img2, mask=None):
        """Calcula el índice de similitud estructural (SSIM) entre dos imágenes."""
        # Convertir a escala de grises
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Si hay máscara, aplicar solo a la región de interés
        if mask is not None:
            gray1 = cv2.bitwise_and(gray1, gray1, mask=mask)
            gray2 = cv2.bitwise_and(gray2, gray2, mask=mask)
        
        # Calcular SSIM
        score, _ = ssim(gray1, gray2, full=True)
        return max(0, score)  # Asegurar que no sea negativo
    
    def _comparar_histogramas(self, img1, img2, mask=None):
        """Compara los histogramas de color de dos imágenes."""
        # Calcular histogramas para cada canal BGR
        similitud_total = 0
        
        for i in range(3):  # BGR channels
            # Usar máscara si está disponible para ignorar el fondo
            hist1 = cv2.calcHist([img1], [i], mask, [256], [0, 256])
            hist2 = cv2.calcHist([img2], [i], mask, [256], [0, 256])
            
            # Normalizar histogramas
            hist1 = cv2.normalize(hist1, hist1).flatten()
            hist2 = cv2.normalize(hist2, hist2).flatten()
            
            # Comparar usando correlación (mejor que chi-cuadrado para este caso)
            similitud = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            similitud_total += similitud
        
        # Promediar los 3 canales
        return max(0, similitud_total / 3)
    
    def _comparar_features(self, img1, img2, mask=None):
        """
        Detecta y compara características únicas usando ORB.
        ORB detecta puntos clave como patrones de anillos, nudos, etc.
        """
        # Convertir a escala de grises
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Detectar keypoints y descriptores (usar máscara para ignorar fondo)
        kp1, des1 = self.orb.detectAndCompute(gray1, mask)
        kp2, des2 = self.orb.detectAndCompute(gray2, mask)
        
        if des1 is None or des2 is None or len(des1) < 10 or len(des2) < 10:
            # Pocas características detectadas
            return 0.0, 0
        
        # Hacer matching de características
        matches = self.bf_matcher.match(des1, des2)
        
        # Ordenar por distancia (menor distancia = mejor match)
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Tomar solo los mejores matches (umbral de distancia)
        good_matches = [m for m in matches if m.distance < 50]
        
        num_coincidencias = len(good_matches)
        max_coincidencias = min(len(kp1), len(kp2))
        
        if max_coincidencias == 0:
            return 0.0, 0
        
        # Calcular ratio de matches buenos
        similitud_features = num_coincidencias / max_coincidencias
        
        return min(1.0, similitud_features), num_coincidencias
    
    def _calcular_mse(self, img1, img2, mask=None):
        """Calcula el Mean Squared Error entre dos imágenes."""
        # Convertir a escala de grises
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Si hay máscara, considerar solo los píxeles dentro de la máscara
        if mask is not None:
            # Aplicar máscara
            gray1_masked = gray1[mask > 0]
            gray2_masked = gray2[mask > 0]
            if len(gray1_masked) > 0 and len(gray2_masked) > 0:
                mse = np.mean((gray1_masked.astype(float) - gray2_masked.astype(float)) ** 2)
                return mse
        
        # Calcular MSE sin máscara
        mse = np.mean((gray1.astype(float) - gray2.astype(float)) ** 2)
        return mse
    
    def _interpretar_ssim(self, valor):
        """Interpreta el valor de SSIM."""
        if valor >= 0.90:
            return "Estructuras muy similares - Patrones de anillos casi idénticos"
        elif valor >= 0.75:
            return "Estructuras similares - Patrones compatibles"
        elif valor >= 0.60:
            return "Estructuras moderadamente similares"
        else:
            return "Estructuras diferentes"
    
    def _interpretar_histograma(self, valor):
        """Interpreta el valor de similitud de histograma."""
        if valor >= 0.90:
            return "Tonalidades de madera muy similares"
        elif valor >= 0.75:
            return "Tonalidades compatibles"
        elif valor >= 0.60:
            return "Tonalidades moderadamente similares"
        else:
            return "Tonalidades diferentes"
    
    def _interpretar_features(self, valor, num_coincidencias):
        """Interpreta el matching de características."""
        if num_coincidencias >= 50:
            return f"Múltiples patrones únicos coincidentes ({num_coincidencias} matches)"
        elif num_coincidencias >= 25:
            return f"Varios patrones coincidentes ({num_coincidencias} matches)"
        elif num_coincidencias >= 10:
            return f"Algunos patrones coincidentes ({num_coincidencias} matches)"
        else:
            return f"Pocos patrones coincidentes ({num_coincidencias} matches)"


def comparar_cortes_transversales(ruta_foto_original, ruta_foto_recepcion):
    """
    Función de conveniencia para comparar dos fotos de cortes transversales.
    
    Args:
        ruta_foto_original (str): Ruta de la foto tomada por el titular
        ruta_foto_recepcion (str): Ruta de la foto tomada en el centro
    
    Returns:
        dict: Resultado de la comparación con similitud_porcentaje y detalles
    """
    comparador = ComparadorImagenes()
    return comparador.comparar_imagenes(ruta_foto_original, ruta_foto_recepcion)
