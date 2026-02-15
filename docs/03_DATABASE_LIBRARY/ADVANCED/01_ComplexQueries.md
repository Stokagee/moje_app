# Complex Queries (ADVANCED)

## Learning Objectives
- [ ] Write JOIN queries for data validation
- [ ] Use aggregate functions effectively
- [ ] Implement subqueries and CTEs
- [ ] Handle JSON data in queries
- [ ] Use window functions for analysis
- [ ] Apply complex filtering patterns

---

## Overview

Complex queries allow sophisticated data validation and testing. This guide covers advanced SQL patterns for Robot Framework Database Library testing.

---

## 1. JOIN Queries

### Pattern: INNER JOIN for Related Data

```robotframework
*** Keywords ***
Get Form With Attachments
    [Documentation]    Get form and its attachments
    [Arguments]    ${form_id}

    # Join form_data with attachments
    ${query}=    Set Variable
    ...    SELECT f.id, f.email, a.filename, a.content_type
    ...    FROM form_data f
    ...    INNER JOIN attachments a ON f.id = a.form_data_id
    ...    WHERE f.id = ${form_id}

    ${result}=    Query    ${query}

    ${count}=    Get Length    ${result}
    Log    ✅ Found ${count} attachments for form ${form_id}

    [Return]    ${result}
```

**Use Cases:**
- Verify foreign key relationships
- Validate related data consistency
- Count related records

---

### Pattern: LEFT JOIN for Optional Relations

```robotframework
*** Keywords ***
Get Forms With Attachment Count
    [Documentation]    Count attachments per form (includes forms with 0)

    ${query}=    Set Variable
    ...    SELECT f.id, f.email, COUNT(a.id) as attachment_count
    ...    FROM form_data f
    ...    LEFT JOIN attachments a ON f.id = a.form_data_id
    ...    GROUP BY f.id, f.email
    ...    ORDER BY attachment_count DESC

    ${result}=    Query    ${query}
    [Return]    ${result}
```

**Use Cases:**
- Find forms without attachments
- Aggregate related data
- Include optional relationships

---

### Pattern: Multiple JOINs

```robotframework
*** Keywords ***
Get Full Order Details
    [Documentation]    Join multiple tables for complete data
    [Arguments]    ${order_id}

    ${query}=    Set Variable
    ...    SELECT o.id as order_id, o.status,
    ...    c.name as courier_name, c.email as courier_email,
    ...    cu.name as customer_name
    ...    FROM orders o
    ...    LEFT JOIN couriers c ON o.courier_id = c.id
    ...    LEFT JOIN customers cu ON o.customer_id = cu.id
    ...    WHERE o.id = ${order_id}

    ${result}=    Query    ${query}

    # Verify joined data
    Should Not Be Empty    ${result}
    Log    Order ${result}[0][order_id]} assigned to ${result}[0][courier_name]

    [Return]    ${result}
```

---

## 2. Aggregate Functions

### Pattern: COUNT with GROUP BY

```robotframework
*** Keywords ***
Count Forms By Gender
    [Documentation]    Count forms per gender category

    ${query}=    Set Variable
    ...    SELECT gender, COUNT(*) as count
    ...    FROM form_data
    ...    GROUP BY gender
    ...    ORDER BY count DESC

    ${result}=    Query    ${query}

    # Log breakdown
    FOR    ${row}    IN    @{result}
        Log    ${row}[gender]: ${row}[count} forms
    END

    [Return]    ${result}
```

---

### Pattern: Multiple Aggregates

```robotframework
*** Keywords ***
Get Order Statistics
    [Documentation]    Calculate various order metrics

    ${query}=    Set Variable
    ...    SELECT
    ...    COUNT(*) as total_orders,
    ...    COUNT(*) FILTER (WHERE status = 'DELIVERED') as delivered,
    ...    COUNT(*) FILTER (WHERE status = 'PENDING') as pending,
    ...    COUNT(*) FILTER (WHERE is_vip = true) as vip_orders
    ...    FROM orders

    ${result}=    Query    ${query}
    ${row}=    Get From List    ${result}    0

    Log    📊 Order Statistics:
    Log    - Total: ${row}[total_orders]
    Log    - Delivered: ${row}[delivered]
    Log    - Pending: ${row}[pending]
    Log    - VIP: ${row}[vip_orders]

    [Return]    ${row}
```

---

### Pattern: HAVING Clause

```robotframework
*** Keywords ***
Find Popular Names
    [Documentation]    Find names appearing more than threshold times

    [Arguments]    ${min_occurrences}

    ${query}=    Set Variable
    ...    SELECT first_name, COUNT(*) as count
    ...    FROM form_data
    ...    GROUP BY first_name
    ...    HAVING COUNT(*) > ${min_occurrences}
    ...    ORDER BY count DESC

    ${result}=    Query    ${query}

    Log    Names appearing more than ${min_occurrences} times:
    FOR    ${row}    IN    @{result}
        Log    - ${row}[first_name]: ${row}[count] times
    END

    [Return]    ${result}
```

---

## 3. Subqueries

### Pattern: Correlated Subquery

```robotframework
*** Keywords ***
Find Forms Above Average
    [Documentation]    Find forms with more than average phone length

    ${query}=    Set Variable
    ...    SELECT id, first_name, LENGTH(phone) as phone_length
    ...    FROM form_data
    ...    WHERE LENGTH(phone) > (
    ...        SELECT AVG(LENGTH(phone))
    ...        FROM form_data
    ...    )

    ${result}=    Query    ${query}

    Log    Forms with above-average phone length: ${len(${result})}

    [Return]    ${result}
```

---

### Pattern: EXISTS Subquery

```robotframework
*** Keywords ***
HasCourierAssigned
    [Documentation]    Check if order has courier using EXISTS

    [Arguments]    ${order_id}

    ${query}=    Set Variable
    ...    SELECT o.id
    ...    FROM orders o
    ...    WHERE o.id = ${order_id}
    ...    AND EXISTS (
    ...        SELECT 1
    ...        FROM dispatch_logs
    ...        WHERE order_id = ${order_id} AND action = 'auto_assigned'
    ...    )

    ${result}=    Query    ${query}
    ${has_courier}=    Set Variable    ${len(${result}) > 0

    [Return]    ${has_courier}
```

---

### Pattern: IN Subquery

```robotframework
*** Keywords ***
Get FormsIn TestSet
    [Documentation]    Get forms that match test criteria

    ${query}=    Set Variable
    ...    SELECT * FROM form_data
    ...    WHERE email IN (
    ...        SELECT email FROM test_emails WHERE active = true
    ...    )

    ${result}=    Query    ${query}
    [Return]    ${result}
```

---

## 4. Common Table Expressions (CTEs)

### Pattern: CTE for Readability

```robotframework
*** Keywords ***
GetFormsWithAttachments
    [Documentation]    Use CTE to simplify complex query

    ${query}=    Set Variable
    ...    WITH forms_with_attachments AS (
    ...        SELECT f.id, f.email, COUNT(a.id) as attachment_count
    ...        FROM form_data f
    ...        LEFT JOIN attachments a ON f.id = a.form_data_id
    ...        GROUP BY f.id, f.email
    ...    )
    ...    SELECT * FROM forms_with_attachments
    ...    WHERE attachment_count > 0

    ${result}=    Query    ${query}
    [Return]    ${result}
```

**Benefits:**
- More readable queries
- Breaks complex logic into steps
- Easier to maintain

---

### Pattern: Multiple CTEs

```robotframework
*** Keywords ***
GetOrderStatistics
    [Documentation]    Use multiple CTEs for breakdown

    ${query}=    Set Variable
    ...    WITH order_counts AS (
    ...        SELECT COUNT(*) as total,
    ...               COUNT(*) FILTER (WHERE status = 'DELIVERED') as delivered,
    ...               COUNT(*) FILTER (WHERE is_vip = true) as vip
    ...        FROM orders
    ...    ),
    ...    courier_stats AS (
    ...        SELECT c.id, c.name, COUNT(o.id) as assigned_orders
    ...        FROM couriers c
    ...        LEFT JOIN orders o ON c.id = o.courier_id
    ...        GROUP BY c.id, c.name
    ...    )
    ...    SELECT
    ...        (SELECT total FROM order_counts) as total_orders,
    ...        (SELECT delivered FROM order_counts) as delivered_orders,
    ...        (SELECT vip FROM order_counts) as vip_orders,
    ...        (SELECT COUNT(*) FROM courier_stats WHERE assigned_orders > 0) as active_couriers
    ...    FROM order_counts

    ${result}=    Query    ${query}
    ${stats}=    Get From List    ${result}    0

    Log    📊 Order Statistics:
    Log    - Total: ${stats}[total_orders]
    Log    - Delivered: ${stats}[delivered_orders]
    Log    - VIP: ${stats}[vip_orders]
    Log    - Active couriers: ${stats}[active_couriers]

    [Return]    ${stats}
```

---

## 5. JSON Data Handling

### Pattern: Query JSON Fields

```robotframework
*** Keywords ***
GetCourierTags
    [Documentation]    Extract tags from JSON field

    ${query}=    Set Variable
    ...    SELECT id, name, tags
    ...    FROM couriers
    ...    WHERE tags->>'vip' = 'true'
    ...    ORDER BY name

    ${result}=    Query    ${query}

    FOR    ${row}    IN    @{result}
        Log    VIP Courier: ${row}[name]
    END

    [Return]    ${result}
```

**Note:** PostgreSQL JSON operators:
- `->>` get JSON value as text
- `->` get JSON value as JSON
- `@>` check if key exists
- `?` check if JSON value is valid

---

### Pattern: JSON Array Operations

```robotframework
*** Keywords ***
CheckHasRequiredTag
    [Documentation]    Check if JSON array contains tag
    [Arguments]    ${courier_id}    ${required_tag}

    ${query}=    Set Variable
    ...    SELECT COUNT(*) > 0 as has_tag
    ...    FROM couriers
    ...    WHERE id = ${courier_id}
    ...    AND tags @> '${required_tag}'

    ${result}=    Query    ${query}
    ${has_tag}=    Set Variable    ${result}[0][has_tag]

    [Return]    ${has_tag}
```

---

## 6. Window Functions

### Pattern: ROW_NUMBER for Ranking

```robotframework
*** Keywords ***
GetTopFormsByEmail
    [Documentation]    Get oldest form per unique email

    ${query}=    Set Variable
    ...    WITH ranked_forms AS (
    ...        SELECT
    ...            id,
    ...            email,
    ...            ROW_NUMBER() OVER (PARTITION BY email ORDER BY id ASC) as rn
    ...        FROM form_data
    ...    )
    ...    SELECT id, email
    ...    FROM ranked_forms
    ...    WHERE rn = 1
    ...    ORDER BY email

    ${result}=    Query    ${query}
    [Return]    ${result}
```

---

### Pattern: LAG/LEAD for Comparison

```robotframework
*** Keywords ***
CompareOrderCounts
    [Documentation]    Compare current vs previous period

    ${query}=    Set Variable
    ...    WITH monthly_counts AS (
    ...        SELECT
    ...            DATE_TRUNC('month', created_at) as month,
    ...            COUNT(*) as order_count,
    ...            LAG(COUNT(*), 1) OVER (ORDER BY DATE_TRUNC('month', created_at)) as prev_count
    ...        FROM orders
    ...        WHERE created_at >= NOW() - INTERVAL '6 months'
    ...        GROUP BY DATE_TRUNC('month', created_at)
    ...    )
    ...    SELECT
    ...        month,
    ...        order_count,
    ...        prev_count,
    ...        order_count - COALESCE(prev_count, 0) as growth
    ...    FROM monthly_counts
    ...    ORDER BY month DESC

    ${result}=    Query    ${query}

    FOR    ${row}    IN    @{result}
        Log    📅 ${row}[month]}: ${row}[order_count]} orders (growth: ${row}[growth]})
    END

    [Return]    ${result}
```

---

## 7. Conditional Aggregation

### Pattern: CASE WHEN

```robotframework
*** Keywords ***
CategorizeOrderStatus
    [Documentation]    Group orders into categories

    ${query}=    Set Variable
    ...    SELECT
    ...        COUNT(*) as total,
    ...        COUNT(*) FILTER (WHERE status = 'CREATED') as created,
    ...        COUNT(*) FILTER (WHERE status = 'ASSIGNED') as assigned,
    ...        COUNT(*) FILTER (WHERE status IN ('PICKED', 'DELIVERED')) as completed,
    ...        COUNT(*) FILTER (WHERE status = 'CANCELLED') as cancelled
    ...    FROM orders

    ${result}=    Query    ${query}
    ${row}=    Get From List    ${result}    0

    &{categories}=    Create Dictionary
    ...    total=${row}[total]
    ...    created=${row}[created]
    ...    assigned=${row}[assigned]
    ...    completed=${row}[completed]
    ...    cancelled=${row}[cancelled]

    Log    📊 Order Categories: ${categories}

    [Return]    ${categories}
```

---

### Pattern: CASE in SELECT

```robotframework
*** Keywords ***
GetOrderStatusDisplay
    [Documentation]    Get user-friendly status name

    ${query}=    Set Variable
    ...    SELECT
    ...        id,
    ...        CASE
    ...            WHEN status = 'CREATED' THEN 'Nová'
    ...            WHEN status = 'ASSIGNED' THEN 'Přiřazeno'
    ...            WHEN status = 'PICKED' THEN 'Vyzvedeno'
    ...            WHEN status = 'DELIVERED' THEN 'Doručeno'
    ...            WHEN status = 'CANCELLED' THEN 'Zrušeno'
    ...            ELSE status
    ...        END as status_cz
    ...    FROM orders
    ...    WHERE id = ${order_id}

    ${result}=    Query    ${query}
    [Return]    ${result}[0][status_cz]
```

---

## 8. Advanced Filtering

### Pattern: Composite Conditions

```robotframework
*** Keywords ***
FindPendingVIPOrders
    [Documentation]    Complex filtering with multiple conditions

    ${query}=    Set Variable
    ...    SELECT * FROM orders
    ...    WHERE status = 'PENDING'
    ...    AND is_vip = true
    ...    AND created_at > NOW() - INTERVAL '1 hour'
    ...    AND (
    ...        pickup_lat IS NOT NULL
    ...        AND pickup_lng IS NOT NULL
    ...    )
    ...    ORDER BY created_at ASC
    ...    LIMIT 50

    ${result}=    Query    ${query}
    [Return]    ${result}
```

---

### Pattern: Pattern Matching

```robotframework
*** Keywords ***
FindByEmailPattern
    [Documentation]    Find records matching email pattern

    ${query}=    Set Variable
    ...    SELECT * FROM form_data
    ...    WHERE email ~ '.*@test\.example\.com$'
    ...    ORDER BY email

    ${result}=    Query    ${query}
    [Return]    ${result}
```

**PostgreSQL Pattern Operators:**
- `~` - matches pattern (case sensitive)
- `~*` - matches pattern (case insensitive)
- `!~` - does not match pattern
- `LIKE` - simple wildcard matching (% and _)

---

## 9. Date/Time Queries

### Pattern: Date Range Queries

```robotframework
*** Keywords ***
GetOrdersFromLastWeek
    [Documentation]    Get orders from last 7 days

    ${query}=    Set Variable
    ...    SELECT * FROM orders
    ...    WHERE created_at >= NOW() - INTERVAL '7 days'
    ...    ORDER BY created_at DESC

    ${result}=    Query    ${query}
    [Return]    ${result}
```

---

### Pattern: Date Truncation

```robotframework
*** Keywords ***
GetDailyOrderCounts
    [Documentation]    Count orders by day

    ${query}=    Set Variable
    ...    SELECT
    ...        DATE_TRUNC('day', created_at)::date as date,
    ...        COUNT(*) as count
    ...    FROM orders
    ...    WHERE created_at >= NOW() - INTERVAL '30 days'
    ...    GROUP BY DATE_TRUNC('day', created_at)::date
    ...    ORDER BY date DESC

    ${result}=    Query    ${query}
    [Return]    ${result}
```

---

## 10. Query Composition Patterns

### Pattern: Build Query Dynamically

```robotframework
*** Keywords ***
BuildDynamicQuery
    [Documentation]    Build query based on parameters
    [Arguments]    &{filters}

    ${select}=    Set Variable    SELECT * FROM form_data
    ${where_clauses}=    Create List

    # Add filters dynamically
    IF    ${filters}[status] != ${EMPTY}
        ${clause}=    Set Variable    status = '${filters}[status]'
        Append To List    ${where_clauses}    ${clause}
    END

    IF    ${filters}[email] != ${EMPTY}
        ${clause}=    Set Variable    email LIKE '%${filters}[email]%'
        Append To List    ${where_clauses}    ${clause}
    END

    # Build WHERE clause
    ${where}=    Set Variable    ${EMPTY}
    FOR    ${i}    IN RANGE    ${where_clauses.__len__}
        ${separator}=    Set Variable IF    ${i} > 0    AND
        ${where}=    Catenate    ${where}    ${separator}    ${where_clauses}[${i}]
    END

    # Build full query
    ${query}=    Set Variable    ${select}
    IF    ${where} != ${EMPTY}
        ${query}=    Catenate    ${query}    WHERE    ${where}
    END

    Log    Executing query: ${query}

    ${result}=    Query    ${query}
    [Return]    ${result}
```

---

## Complex Query Best Practices

| Pattern | Use Case | Key Benefit |
|---------|----------|-------------|
| JOIN | Related tables | Validate relationships |
| CTE | Complex queries | Improved readability |
| EXISTS | Existence check | Efficient checking |
| GROUP BY | Aggregation | Summarize data |
| HAVING | Filter aggregates | Post-aggregate filtering |
| Window functions | Ranking/analysis | Complex calculations |
| JSON operators | NoSQL data | Query structured data |
| CASE WHEN | Conditional logic | User-friendly output |

---

## Query Testing Patterns

### Pattern: Verify Query Results

```robotframework
*** Keywords ***
ValidateComplexQuery
    [Documentation]    Verify query returns expected structure

    ${query}=    Set Variable
    ...    SELECT f.id, f.email, COUNT(a.id) as attachment_count
    ...    FROM form_data f
    ...    LEFT JOIN attachments a ON f.id = a.form_data_id
    ...    GROUP BY f.id, f.email
    ...    ORDER BY attachment_count DESC
    ...    LIMIT 10

    ${result}=    Query    ${query}

    # Verify structure
    FOR    ${row}    IN    @{result}
        Dictionary Should Contain Key    ${row}    id
        Dictionary Should Contain Key    ${row}    email
        Dictionary Should Contain Key    ${row}    attachment_count
    END

    # Verify no NULLs in key fields
    FOR    ${row}    IN    @{result}
        Should Not Be Equal    ${row}[id]    ${NONE}
        Should Not Be Equal    ${row}[email]    ${NONE}
    END

    Log    ✅ Query validation passed
    [Return]    ${result}
```

---

## References

- [PostgreSQL SQL Reference](https://www.postgresql.org/docs/current/sql-syntax.html)
- [Window Functions](https://www.postgresql.org/docs/current/functions-window.html)
- [JSON Functions](https://www.postgresql.org/docs/current/functions-json.html)
- [Performance Patterns](00_PerformancePatterns.md)
