# Comparación de Imágenes de Cortes Transversales

## Descripción

Este sistema compara automáticamente las fotos de cortes transversales de madera para verificar que la troza recibida en el centro de transformación sea la misma que registró el titular en origen.

## Cómo Funciona

### 1. Registro del Titular
Cuando el titular registra un trozo de madera, debe subir una foto del **corte transversal** que muestre claramente:
- Anillos de crecimiento
- Patrones únicos de la madera
- Color y textura de la especie

Esta foto se guarda en la base de datos asociada al código único del trozo.

### 2. Recepción en el Centro
Cuando la troza llega al centro de transformación, el operador:
1. Ingresa el código QR del trozo
2. Sube una nueva foto del **mismo corte transversal**
3. El sistema automáticamente:
   - Recupera la foto original del titular
   - Compara ambas imágenes usando múltiples algoritmos
   - Calcula un porcentaje de similitud
   - Determina si coinciden o no

### 3. Algoritmos de Comparación

El sistema usa **4 métricas diferentes** para máxima precisión:

#### A. SSIM - Structural Similarity Index (Peso: 40%)
- **Qué mide**: Similitud estructural entre las imágenes
- **Por qué es importante**: Detecta patrones de anillos de crecimiento, que son únicos para cada árbol
- **Rango**: 0% (completamente diferente) a 100% (idéntico)

#### B. Histogramas de Color (Peso: 25%)
- **Qué mide**: Distribución de colores en la imagen
- **Por qué es importante**: Cada especie de madera tiene tonalidades características
- **Método**: Compara los 3 canales BGR (Blue, Green, Red)

#### C. ORB Feature Matching (Peso: 35%)
- **Qué mide**: Características únicas y puntos clave en la imagen
- **Por qué es importante**: Detecta patrones únicos como nudos, irregularidades, y detalles específicos de cada trozo
- **Método**: Encuentra hasta 500 puntos clave y los compara entre imágenes

#### D. MSE - Mean Squared Error (Informativo)
- **Qué mide**: Error promedio entre píxeles
- **Uso**: Métrica complementaria, menor valor = más similitud

## Interpretación de Resultados

### Niveles de Similitud

| Porcentaje | Nivel | Decisión | Interpretación |
|------------|-------|----------|----------------|
| ≥ 75% | ALTA | ✓ Coincide | Es muy probable que sea la misma troza |
| 60-74% | MEDIA | ✓ Coincide | Posiblemente sea la misma troza |
| 45-59% | BAJA | ✗ No coincide | Requiere verificación adicional manual |
| < 45% | MUY BAJA | ✗ No coincide | Probablemente NO es la misma troza |

### Criterios de Aprobación

Para que un trozo sea **APROBADO**, debe cumplir AMBAS condiciones:

1. ✓ **Legalidad**: La especie debe estar en el inventario OSINFOR con plan de manejo vigente
2. ✓ **Autenticidad**: La foto debe tener ≥60% de similitud con la original

Si la foto no coincide pero la madera es legal, el resultado será **RECHAZADO** con el motivo:
> "Legal pero la foto del corte NO coincide con la original"

## Detalles Técnicos

### Preprocesamiento
- Las imágenes se redimensionan a 512×512 píxeles para comparación consistente
- Se convierten a escala de grises para análisis estructural
- Se normalizan los histogramas

### Robustez del Sistema
El sistema es robusto ante:
- ✓ Diferentes ángulos de la cámara (hasta cierto grado)
- ✓ Variaciones de iluminación
- ✓ Diferentes resoluciones de cámara
- ✓ Ligeras rotaciones de la imagen

No es robusto ante:
- ✗ Fotos extremadamente borrosas
- ✗ Obstrucciones que cubran la mayoría del corte
- ✗ Comparar cortes de diferentes alturas del mismo árbol
- ✗ Madera deteriorada o dañada significativamente

## Recomendaciones para Mejores Resultados

### Al Tomar la Foto Original (Titular)
1. Limpiar el corte de aserrín y suciedad
2. Tomar la foto de frente, perpendicular al corte
3. Asegurar buena iluminación uniforme
4. Mostrar TODO el diámetro del corte
5. Evitar sombras pronunciadas
6. Enfocar bien la imagen

### Al Tomar la Foto de Verificación (Centro)
1. Buscar el **mismo corte** que aparece en la foto original
2. Intentar el mismo ángulo y distancia
3. Usar iluminación similar
4. Limpiar el corte si está sucio
5. Si el corte está deteriorado, tomar foto de la parte mejor conservada

## Ejemplos de Uso

### Caso 1: Madera Legal y Auténtica
```
Resultado: APROBADO
├─ Legalidad: ✓ Caoba en plan PM-123-2023 (VIGENTE)
└─ Autenticidad: ✓ 89.5% similitud (ALTA)
   ├─ SSIM: 91.2%
   ├─ Histograma: 88.5%
   ├─ Features: 89.1% (156 matches)
   └─ MSE: 234.5
```

### Caso 2: Madera Legal pero Foto No Coincide
```
Resultado: RECHAZADO
├─ Legalidad: ✓ Cedro en plan PM-456-2024 (VIGENTE)
└─ Autenticidad: ✗ 42.3% similitud (MUY BAJA)
   Motivo: Legal pero la foto del corte NO coincide con la original
```

### Caso 3: Madera Ilegal
```
Resultado: RECHAZADO
├─ Legalidad: ✗ Especie no está en ningún plan vigente
└─ Autenticidad: N/A
   Motivo: La especie 'Pino' no está registrada en ningún plan de manejo vigente
```

## Limitaciones Conocidas

1. **Cortes diferentes**: Si el centro fotografía un corte diferente al del titular, la similitud será baja
2. **Deterioro**: Si la madera se deterioró significativamente durante el transporte, puede afectar la similitud
3. **Condiciones extremas**: Fotos muy oscuras, borrosas o con obstrucciones pueden dar falsos negativos

## Mejoras Futuras Posibles

- [ ] Machine Learning para aprender patrones específicos de cada especie
- [ ] Detección automática de región de interés (ROI)
- [ ] Corrección automática de iluminación y rotación
- [ ] Alertas para fotos de mala calidad antes de procesarlas
- [ ] Base de datos de "huellas digitales" de trozas conocidas

## Soporte Técnico

Si el sistema rechaza incorrectamente una troza legítima:
1. Verificar que la foto sea del mismo corte
2. Revisar la calidad de ambas fotos
3. Contactar al titular para obtener foto alternativa del mismo corte
4. En última instancia, realizar verificación manual
