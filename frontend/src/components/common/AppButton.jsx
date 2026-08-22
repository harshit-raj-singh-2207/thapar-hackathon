import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, View } from 'react-native';

export default function AppButton({
  title,
  onPress,
  variant = 'primary', // 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost' | 'success'
  size = 'md', // 'sm' | 'md' | 'lg'
  disabled = false,
  loading = false,
  icon,
  style,
  textStyle,
}) {
  const getButtonStyles = () => {
    const stylesArr = [styles.base, styles[size]];

    switch (variant) {
      case 'secondary':
        stylesArr.push(styles.secondary);
        break;
      case 'danger':
        stylesArr.push(styles.danger);
        break;
      case 'success':
        stylesArr.push(styles.success);
        break;
      case 'outline':
        stylesArr.push(styles.outline);
        break;
      case 'ghost':
        stylesArr.push(styles.ghost);
        break;
      case 'primary':
      default:
        stylesArr.push(styles.primary);
        break;
    }

    if (disabled || loading) {
      stylesArr.push(styles.disabled);
    }

    if (style) {
      stylesArr.push(style);
    }

    return stylesArr;
  };

  const getTextStyles = () => {
    const textStylesArr = [styles.textBase, styles[`text_${size}`]];

    switch (variant) {
      case 'secondary':
        textStylesArr.push(styles.textSecondary);
        break;
      case 'outline':
      case 'ghost':
        textStylesArr.push(styles.textOutline);
        break;
      case 'danger':
      case 'success':
      case 'primary':
      default:
        textStylesArr.push(styles.textPrimary);
        break;
    }

    if (disabled) {
      textStylesArr.push(styles.textDisabled);
    }

    if (textStyle) {
      textStylesArr.push(textStyle);
    }

    return textStylesArr;
  };

  const getLoaderColor = () => {
    if (variant === 'outline' || variant === 'ghost') return '#2563EB';
    if (variant === 'secondary') return '#0F172A';
    return '#FFFFFF';
  };

  return (
    <TouchableOpacity
      style={getButtonStyles()}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.85}
      accessibilityRole="button"
    >
      {loading ? (
        <ActivityIndicator size="small" color={getLoaderColor()} />
      ) : (
        <View style={styles.contentRow}>
          {icon && <View style={styles.iconContainer}>{icon}</View>}
          <Text style={getTextStyles()}>{title}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
  },
  contentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    marginRight: 8,
  },
  sm: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 10,
  },
  md: {
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 14,
  },
  lg: {
    paddingVertical: 15,
    paddingHorizontal: 24,
    borderRadius: 16,
  },
  primary: {
    backgroundColor: '#2563EB',
    shadowColor: '#2563EB',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 3,
  },
  secondary: {
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  success: {
    backgroundColor: '#059669',
    shadowColor: '#059669',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 3,
  },
  danger: {
    backgroundColor: '#DC2626',
    shadowColor: '#DC2626',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4,
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: '#2563EB',
  },
  ghost: {
    backgroundColor: 'transparent',
  },
  disabled: {
    opacity: 0.55,
    shadowOpacity: 0,
    elevation: 0,
  },
  textBase: {
    fontWeight: '800',
    letterSpacing: 0.2,
  },
  text_sm: {
    fontSize: 12,
  },
  text_md: {
    fontSize: 14,
  },
  text_lg: {
    fontSize: 16,
  },
  textPrimary: {
    color: '#FFFFFF',
  },
  textSecondary: {
    color: '#0F172A',
  },
  textOutline: {
    color: '#2563EB',
  },
  textDisabled: {
    color: '#94A3B8',
  },
});
