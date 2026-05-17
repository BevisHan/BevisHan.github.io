---
title: Spring Cloud Nacos 配置刷新失败排查记录
date: 2026-05-01
categories: [踩坑实录]
tags: [Spring Cloud, Nacos, 配置中心]
---

## 问题

Spring Cloud 项目中，Nacos 配置中心改了配置值，但应用没有自动刷新。`@RefreshScope` 已经加了，但还是拿不到新值。

## 排查过程

### 1. 确认配置变更是否推送成功

查看 Nacos 控制台 → 配置管理 → 历史版本，确认配置确实已经修改并发布了。

### 2. 检查依赖版本

项目中使用的 `spring-cloud-starter-alibaba-nacos-config` 版本是 `2021.1`，理论上支持自动刷新。

### 3. 发现问题：自定义 PropertySource

项目中有一段代码自定义了 `PropertySourceLocator`，在 Nacos 之后加载配置：

```java
@Component
public class CustomPropertySourceLocator implements PropertySourceLocator {
    @Override
    public PropertySource<?> locate(Environment environment) {
        // 这里加载的配置会覆盖 Nacos 的配置
        Map<String, Object> source = new HashMap<>();
        source.put("my.config.value", "old-value");
        return new MapPropertySource("custom", source);
    }
}
```

这个自定义 `PropertySourceLocator` 的优先级高于 Nacos，导致 Nacos 的新值被覆盖了。

## 解决方案

修改 `CustomPropertySourceLocator` 的 `order`，让它的优先级低于 Nacos：

```java
@Component
@Order(Ordered.LOWEST_PRECEDENCE)  // 降低优先级
public class CustomPropertySourceLocator implements PropertySourceLocator {
    // ...
}
```

或者直接用 `@Value` + `@RefreshScope` 的方式，避免自定义配置源覆盖。

## 总结排查方向

下次遇到类似问题，按这个顺序排查：

1. Nacos 配置是否确实推送了（控制台历史版本确认）
2. 是否加了 `@RefreshScope`（最常见的遗漏）
3. 是否有自定义 PropertySource 覆盖了 Nacos 的值
4. `bootstrap.yml` 中的配置是否正确
